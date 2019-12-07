from troposphere import Template, constants, Ref, Parameter, Join
from troposphere.cloudformation import Stack

template = Template(Description='All stacks related to Spunt.be')

template_bucket = template.add_parameter(Parameter(
    'TemplateBucket',
    Type=constants.STRING,
    Default='https://spunt-punt-be-pipeline-buildbucket-1a782efme0ghm.s3.amazonaws.com/',
))

frontend_hosting_template = template.add_parameter(Parameter(
    'FrontendHostingTemplate',
    Type=constants.STRING,
    Default='cloudformation/frontend_hosting.json',
))


def _template_url(template_key):
    return Join('', [Ref(template_bucket), template_key])


template.add_resource(Stack(
    'FrontendHosting',
    TemplateURL=_template_url(Ref(frontend_hosting_template)),
))

f = open("output/spunt_be.json", "w")
f.write(template.to_json())
