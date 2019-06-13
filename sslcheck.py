""" Print certificate chain information for given hostname."""
VERSION = (1, 0, 4)

__title__ = 'sslcheck'
__description__ = 'A simple command line SSL validator'
__url__ = 'http://gitlab.com/radek-sprta/sslcheck'
__download_url__ = 'https://gitlab.com/radek-sprta/sslcheck/repository/archive.tar.gz?ref=master'
__version__ = '.'.join(map(str, VERSION))
__author__ = 'Radek Sprta'
__author_email__ = 'mail@radeksprta.eu'
__license__ = 'MIT License'
__copyright__ = "Copyright 2018 Radek Sprta"

import argparse
import datetime
import socket
from urllib import parse

import certifi
import OpenSSL as ssl

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'
YELLOW = '\033[33m'


class Certificate:
    """SSL certificate."""

    def __init__(self, cert):
        self.cert = cert

    @property
    def cn(self):  # pylint: disable=inconsistent-return-statements
        """Certificate Common Name."""
        for detail in self.subject:
            if 'CN' in detail:
                return detail['CN']

    @property
    def has_expired(self):
        """Return whether certificate has expired."""
        return self.cert.has_expired()

    @property
    def issuer(self):
        """Certificate issuer."""
        return self._decode(self.cert.get_issuer().get_components())

    @property
    def key(self):
        """Certificate key."""
        key = self.cert.get_pubkey()
        types = {
            ssl.crypto.TYPE_RSA: "RSA",
            ssl.crypto.TYPE_DSA: "DSA",
        }
        return (types.get(key.type(), "UNKNOWN"), key.bits())

    @property
    def san(self):
        """Certificate Subject Alternative names."""
        for i in range(self.cert.get_extension_count()):
            extension = self.cert.get_extension(i)
            if extension.get_short_name() == b'subjectAltName':
                return extension.__str__()
        return None

    @property
    def subject(self):
        """Certificate subject."""
        return self._decode(self.cert.get_subject().get_components())

    @property
    def valid_from(self):
        """Certificate notBefore field."""
        return self.prettify_date(self._decode(self.cert.get_notBefore()[:8]))

    @property
    def valid_until(self):
        """Certificate notAfter field."""
        return self.prettify_date(self._decode(self.cert.get_notAfter()[:8]))

    def _decode(self, binary):
        """Return string representation."""
        if isinstance(binary, (str, int)):
            return binary
        elif isinstance(binary, bytes):
            return binary.decode()
        elif isinstance(binary, dict):
            return {self._decode(i): self._decode(v) for i, v in binary.items()}
        elif isinstance(binary, list):
            return [self._decode(i) for i in binary]
        elif isinstance(binary, tuple):
            return {self._decode(binary[0]): self._decode(binary[1])}
        elif binary is None:
            return None
        else:
            raise ValueError('Wrong argument type {}'.format(type(binary)))

    def digest(self, name):
        """Return certificate digest."""
        return self.cert.digest(name)

    @staticmethod
    def prettify_date(date):
        """Prettify date to YYYY-MM-DD format."""
        return datetime.datetime.strptime(date, '%Y%m%d').date()

    @staticmethod
    def render(details):
        """Render dictionary for printing."""
        rendered = []
        for line in details:
            key, value = line.popitem()
            rendered.append('    {}: {}'.format(key, value))
        return '\n'.join(rendered)

    def __eq__(self, other):
        return self.digest("sha256") == other.digest("sha256")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '\n'.join(
            ['Common Name: {}{}{}'.format(YELLOW, self.cn, RESET),
             'Subject Alternative Names: {}{}{}'.format(
                 YELLOW, self.san, RESET),
             'Valid between {}{}{} and {}{}{}'.format(
                 GREEN, self.valid_from, RESET, GREEN, self.valid_until, RESET),
             'Public Key: {}{} {}{}'.format(
                 YELLOW, self.key[0], str(self.key[1]), RESET),
             'Subject:\n{}'.format(self.render(self.subject)),
             'Issuer:\n{}'.format(self.render(self.issuer))])


class CertificateChain:
    """Validate certificate chain."""

    def __init__(self, hostname, server, port=443):
        self.hostname = hostname
        self.connection = SSLConnection(hostname, server, port)

    @property
    def certs(self):
        """Return server certificate for given hostname."""
        return [Certificate(c) for c in self.connection.get_host_certs()]

    @property
    def expiration_date(self):
        """Return server certificate expiration date."""
        return self.server_cert.valid_until

    @property
    def has_expired(self):
        """Return if certificate has expired."""
        return self.server_cert.has_expired

    @property
    def ip(self):
        """Return IP of the server connected to."""
        return self.connection.ip

    @property
    def server_cert(self):
        """Server certificate."""
        return self.certs[0]

    def verify_chain(self):
        """Verify the chain of trust."""
        store = self.connection.context.get_cert_store()
        try:
            # Add intermediate certs into store
            for cert in self.certs[1:]:
                store.add_cert(cert.cert)
            # Verify the chain from server certificate
            ctx_store = ssl.crypto.X509StoreContext(
                store, self.server_cert.cert)
            ctx_store.verify_certificate()
            return True
        except ssl.crypto.X509StoreContextError:
            # Chain is broken
            return False

    def verify_cn(self):
        """Verify common name."""
        star = ['*']
        hostname_stub = self.hostname.split('.')[1:]
        star.extend(hostname_stub)
        wild_hostname = '.'.join(star)

        if self.server_cert.san is None:
            return False
        elif self.hostname in self.server_cert.san:
            return True
        elif wild_hostname in self.server_cert.san:
            return True
        return False

    def __repr__(self):
        return 'CertificateChain({}, {}, {})'.format(self.connection.hostname,
                                                     self.connection.server,
                                                     self.connection.port)

    def __str__(self):
        chain = []
        for i, cert in enumerate(self.certs, 1):
            chain.append('\nCert no.{}'.format(i))
            chain.append(str(cert))
        return '\n'.join(chain)


class SSLConnection:
    """SSL Connection to given host."""

    def __init__(self, hostname, server, port=443):
        self.hostname = hostname
        self.server = server
        self.port = port
        self.context = self.get_context()
        try:
            self.connection = self.connect()
        except ssl.SSL.Error:
            # When server refuses TLSv1
            self.context = self.get_context(method=ssl.SSL.TLSv1_2_METHOD)
            self.connection = self.connect()

    @property
    def ip(self):
        """Return IP of the server connected to."""
        return socket.gethostbyname(self.server)

    def connect(self):
        """Return SSL connection to given hostname."""
        connection = ssl.SSL.Connection(self.context, socket.socket())

        # Set hostname for SNI
        connection.set_tlsext_host_name(self.hostname.encode())

        connection.connect((self.server, self.port))
        connection.do_handshake()
        return connection

    @staticmethod
    def get_context(method=ssl.SSL.TLSv1_METHOD):
        """Get context for SSL."""
        context = ssl.SSL.Context(method)
        context.load_verify_locations(certifi.where())
        return context

    def get_host_certs(self):
        """Return host's certificate chain."""
        return self.connection.get_peer_cert_chain()


def get_opts():
    """Return hostname and server from the list of command arguments."""
    parser = argparse.ArgumentParser(
        description='Get certificate information from server and validate it')
    parser.add_argument('--server', '-s', help='Server to connect to')
    parser.add_argument(
        '--port', '-p', help='Port to connect to', default=443, type=int)
    parser.add_argument('hostname', help='Certificate hostname')
    return parser.parse_args()


def print_chain_header(chain):
    """Print Certificate Chain Header information."""
    # Check common name
    if not chain.verify_cn():
        print('{}{} not in certificate common names!{}'.format(
            RED, chain.hostname, RESET))

    # Check chain of trust
    if chain.verify_chain():
        return 1
    else:
        return -1

    # Check expiration date
    delta = abs((chain.expiration_date - datetime.date.today()).days)
    if chain.has_expired:
        print("{}Server certificate expired on {} ({} days ago).{}".format(
            RED, chain.expiration_date, delta, RESET))
    elif delta > 10:
        print("{}Server certificate will expire on {} (in {} days).{}".format(
            GREEN, chain.expiration_date, delta, RESET))
    else:

        print("{}Server certificate will expire on {} (in {} days).{}".format(
            YELLOW, chain.expiration_date, delta, RESET))


def final_check_certificate(hostname, server, port):
    chain = CertificateChain(hostname, server, port)
    return (print_chain_header(chain))


def main():
    """Main entrance point."""
    opts = get_opts()

    if ('http' in opts.hostname) or ('/' in opts.hostname):
        hostname = parse.urlparse(opts.hostname).netloc
    else:
        hostname = opts.hostname
    server = opts.server if opts.server else hostname
    port = opts.port

    print('Hostname: {}{}{}'.format(YELLOW, hostname, RESET))
    print('Server: {}{}:{}{}'.format(YELLOW, server, port, RESET))
    try:
        chain = CertificateChain(hostname, server, port)
        print('IP Address: {}{}{}\n'.format(YELLOW, chain.ip, RESET))
    except socket.gaierror:
        print("Server {} unavailable".format(server))
    except (OSError, ConnectionRefusedError):
        print('Connection refused. Wrong port?')
    else:
        # Print certificate chain header
        print_chain_header(chain)

        # Print certificate chain details
        print(chain)

# if __name__ == '__main__':
#     main()

