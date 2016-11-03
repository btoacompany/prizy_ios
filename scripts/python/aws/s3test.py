import boto3
import os
aws_access_key_id = "AKIAJXIXL4647ST4BBCA"
aws_secret_access_key = "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"

folder = r"./s3Object"

boto3.setup_default_session(
    aws_secret_access_key=aws_secret_access_key,
    aws_access_key_id=aws_access_key_id,
)

def downloadbucket(bucketName):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(name=bucketName)

    for obj in bucket.objects.iterator():
        if obj.size > 0:
            path = os.path.join(folder,bucketName,obj.key)
            dir = os.path.dirname(path)
            if not os.path.exists(dir):
                os.makedirs(dir)
            print("Downloading",path)
            bucket.download_file(obj.key,path)


if __name__=="__main__":
    s3 = boto3.resource("s3")
    list(map(lambda x : downloadbucket(x.name), s3.buckets.all()))

