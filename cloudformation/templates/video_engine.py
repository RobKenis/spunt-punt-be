from troposphere import Template
from troposphere.s3 import Bucket

template = Template(Description='Video engine for spunt.be')

upload_s3 = template.add_resource(Bucket(
    'UploadS3'
))

f = open("output/video_engine.json", "w")
f.write(template.to_json())
