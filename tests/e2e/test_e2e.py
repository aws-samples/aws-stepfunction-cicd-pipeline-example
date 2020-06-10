# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import pytest
from StepFunctionClient import StepFunctionClient

def test_successful_execution():
    # read environment variables from CodeBuild Project
    aws_region = os.environ['AWS_REGION']
    state_machine_name = os.environ['STATE_MACHINE_NAME']

    client = StepFunctionClient(aws_region=aws_region)

    # start the state machine
    pipeline_metadata = client.start_pipeline_synchronous(
        name=f"{state_machine_name}-Stage",
        input='{\"input\": \"1 20 3\"}'
    )

    expected_output = {'first': '1', 'second': '20', 'third': '3', 'result': 3}

    print(pipeline_metadata)
    execution_arn = pipeline_metadata.get_executionarn()
    execution_metadata = client.get_pipeline_execution_metadata(executionarn=execution_arn)
    execution_output = execution_metadata.get_output()
    json_output = json.loads(execution_output)

    assert(pipeline_metadata.get_status() == 'SUCCEEDED')
    assert(json_output['Payload'] == expected_output)
