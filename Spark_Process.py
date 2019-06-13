import difflib
from pyspark.sql.functions import udf
from pyspark.sql import SparkSession
import numpy as np
def check_intersect(xs):

    @udf("long")
    def _(ys):
        x =  int(difflib.SequenceMatcher(None,xs,list(ys)).ratio()*100)
        return x

    return _

def spark_activity_to_detect(a_list):
    training_data = np.genfromtxt('dataset.csv', delimiter=',', dtype=np.int32)
    inputs = training_data[:,:-1]
    outputs = training_data[:, -1]
    spark= SparkSession.builder.getOrCreate()
    df = spark.createDataFrame(list(zip(inputs.tolist(),outputs.tolist())), ("articles","result"))
    check_col = df.withColumn("check", check_intersect(a_list)("articles"))
    row1 = check_col.agg({"check": "max"}).collect()[0]
    row2 = check_col.select(check_col.check.between(row1["max(check)"],row1["max(check)"]),check_col.result).collect()[0]

    return (row2["result"])
