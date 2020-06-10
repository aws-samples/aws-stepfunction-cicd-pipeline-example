# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import sys
import json
from jinja2 import Template

Lambda_dict = {}
Environment = ""

def read_sm_def (
    sm_def_file: str
) -> dict:
    """
    Reads state machine definition from a file and returns it as a dictionary.

    Parameters:
        sm_def_file (str) = the name of the state machine definition file.

    Returns:
        sm_def_dict (dict) = the state machine definition as a dictionary.
    """

    try:
        with open(f"{sm_def_file}", "r") as f:
            return f.read()
    except IOError as e:
        print("Path does not exist!")
        print(e)
        sys.exit(1)

def template_sm_def (
    sm_def_template: dict
) -> dict:
    Lambda_dict = json.loads(os.environ["Lambda_Func"])
    Environment = os.environ["Environment"]
    if Environment == 'Stage':
        clean_input_function = Lambda_dict["Stage"][0]["CLEANINPUT_FUNCTION"]
        multiply_function = Lambda_dict["Stage"][0]["MULTIPLY_FUNCTION"]
        add_function = Lambda_dict["Stage"][0]["ADD_FUNCTION"]
        subtract_function = Lambda_dict["Stage"][0]["SUBTRACT_FUNCTION"]
        divide_function = Lambda_dict["Stage"][0]["DIVIDE_FUNCTION"]
    else:
        clean_input_function = Lambda_dict["Prod"][0]["CLEANINPUT_FUNCTION"]
        multiply_function = Lambda_dict["Prod"][0]["MULTIPLY_FUNCTION"]
        add_function = Lambda_dict["Prod"][0]["ADD_FUNCTION"]
        subtract_function = Lambda_dict["Prod"][0]["SUBTRACT_FUNCTION"]
        divide_function = Lambda_dict["Prod"][0]["DIVIDE_FUNCTION"]

    tm = Template(sm_def_template)
    msg = tm.render(
        CleanInput=clean_input_function,
        Multiply=multiply_function,
        Subtract=subtract_function,
        Add=add_function,
        Divide=divide_function
    )

    return msg

def template_state_machine(
    sm_def: dict
) -> dict:
    """
    Templates out the CloudFormation for creating a state machine.

    Parameters:
        sm_def (dict) = a dictionary definition of the aws states language state machine.

    Returns:
        templated_cf (dict) = a dictionary definition of the state machine.
    """
    
    templated_cf = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Creates the Step Function State Machine and associated IAM roles and policies",
        "Parameters": {
            "StateMachineName": {
                "Description": "The name of the State Machine",
                "Type": "String"
            }
        },
        "Resources": {
            "StateMachineLambdaRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": "states.amazonaws.com"
                                },
                                "Action": "sts:AssumeRole"
                            }
                        ]
                    },
                    "Policies": [
                        {
                            "PolicyName": {
                                "Fn::Sub": "States-Lambda-Execution-${AWS::StackName}-Policy"
                            },
                            "PolicyDocument": {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": [
                                            "logs:CreateLogStream",
                                            "logs:CreateLogGroup",
                                            "logs:PutLogEvents",
                                            "sns:*"
                                        ],
                                        "Resource": "*"
                                    },
                                    {
                                        "Effect": "Allow",
                                        "Action": [
                                            "lambda:InvokeFunction"
                                        ],
                                        "Resource": "*"
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            "StateMachine": {
                "Type": "AWS::StepFunctions::StateMachine",
                "Properties": {
                    "DefinitionString": sm_def,
                    "RoleArn": {
                        "Fn::GetAtt": [
                            "StateMachineLambdaRole",
                            "Arn"
                        ]
                    },
                    "StateMachineName": {
                        "Ref": "StateMachineName"
                    }
                }
            }
        }
    }

    return templated_cf


sm_def_dict = read_sm_def(
    sm_def_file='sm_def.json'
)

templated_sm_def = template_sm_def(
    sm_def_template=sm_def_dict
)

print(templated_sm_def)

cfm_sm_def = template_state_machine(
    sm_def=templated_sm_def
)

with open("sm_cfm.json", "w") as f:
    f.write(json.dumps(cfm_sm_def))
