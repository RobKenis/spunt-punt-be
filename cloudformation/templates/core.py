from troposphere import Template, Output, Ref, Export, Join, AWS_STACK_NAME
from troposphere.s3 import Bucket

template = Template(Description='Core resources for spunt.be and deployments')

lambda_code_bucket = template.add_resource(Bucket(
    'LambdaCodeBucket',
))

template.add_output(Output(
    "LambdaCodeBucket",
    Description='Name of the bucket where all the lambda code is located.',
    Value=Ref(lambda_code_bucket),
    Export=Export(Join("-", [Ref(AWS_STACK_NAME), 'LambdaCodeBucket-Ref'])),
))


f = open("output/core.json", "w")
f.write(template.to_json())
