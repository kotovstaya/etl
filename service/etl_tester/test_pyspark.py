import pandas as pd
from pyspark.sql import SparkSession

spark = (
    SparkSession
    .builder
    .appName("test")
    .master("spark://spark-master:7077")
    .config('spark.jars.packages', 'org.apache.hadoop:hadoop-aws:3.2.2')
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.fast.upload", 'true')
    .config("spark.sql.files.ignoreMissingFiles", "true")
    .config("spark.delta.logStore.class", "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore")
    .config("spark.network.timeout", "10000s")
    .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
    .config('spark.hadoop.fs.s3a.aws.credentials.provider', 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider')
    .config("spark.hadoop.fs.s3.multiobjectdelete.enable", "true")
    .config("spark.hadoop.fs.s3a.endpoint", "minio:9000")
    .config("spark.hadoop.fs.s3a.access.key", "admin")
    .config("spark.hadoop.fs.s3a.secret.key", "admin123")
    .config("spark.hadoop.fs.s3a.path.style.access", 'true')
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .getOrCreate()
)

df = pd.DataFrame(data={"name": ['aa', 'bb'], "age": [31, 22]})
df = spark.createDataFrame(df)

df.show()

df.write.parquet("s3a://data-science/test.parquet")
spark.read.parquet("s3a://data-science/test.parquet")

df.show()



# from minio import Minio
# from minio.error import S3Error

# client = Minio('minio:9000', access_key='admin',  secret_key='admin123', secure=False)
# print(client)
# client.make_bucket("tst")
# buckets = client.list_buckets()

# print(buckets)

