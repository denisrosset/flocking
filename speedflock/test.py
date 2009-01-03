import externals.S3

AWS_ACCESS_KEY_ID = '1BYZG38150N2CF9TY8R2'
AWS_SECRET_ACCESS_KEY = '9g2GECzSJuS3F6NDv5TqkAgUIGx12ut8Z4NnM6hi'

BUCKET_NAME = 'speedflock'
KEY_NAME = '20081210'

conn = externals.S3.AWSAuthConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

generator = externals.S3.QueryStringAuthGenerator(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

print map(lambda x: x.key, conn.list_bucket(BUCKET_NAME).entries)
