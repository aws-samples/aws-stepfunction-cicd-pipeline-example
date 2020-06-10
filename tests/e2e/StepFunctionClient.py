# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import uuid
import time
import json
from PipelineExecutionMetadata import PipelineExecutionMetadata

class StepFunctionClient():
    """
    This class chains together necessary API calls to AWS and populates model objects.
    
    Attributes:
        client (boto3) = the boto3 client for step functions.
        region (str) = the aws region to create the client in (e.g. 'us-east-1').
    """

    def __init__(self, aws_region: str):
        """
        The constructor for the StepFunctionClient class.

        Parameters:
            region (str) = the aws region to create the client in (e.g. 'us-east-1').
        """

        self.client = boto3.client(
            service_name='stepfunctions', 
            region_name=aws_region
        )
        self.region = aws_region
        self.accountid = boto3.client("sts").get_caller_identity()["Account"]

    def start_pipeline_synchronous (
        self,
        name: str,
        input: str
    ) -> PipelineExecutionMetadata:
        """
        Starts a state machine execution until completion.

        Parameters:
            name (str) = the name of the state machine to execute.
            input (str) = json string representing input to starting state.

        Returns:
            PipelineExecution = an object representing the execution at a high level.
        """

        arn = "arn:aws:states:{}:{}:stateMachine:{}".format(self.region, self.accountid, name)
        print(f"Starting Pipeline with ARN of {arn}")

        response = self.client.start_execution(
            stateMachineArn=arn,
            name=str(uuid.uuid1()),
            input=input
        )

        executionarn = response.get('executionArn')

        print(f"Initial Response: {response}")
        print(f"Waiting for Execution to Complete for Execution ARN {executionarn}")

        while executionarn in str(self.get_running_execution_history(arn)):
            time.sleep(10)

        execution = self.get_pipeline_execution_metadata (
            executionarn=executionarn
        )

        if execution.get_status() == 'RUNNING':
            time.sleep(10)
        
        return self.get_pipeline_execution_metadata (
            executionarn=executionarn
        )

    def get_running_execution_history (
        self,
        smarn: str
    ) -> list:
        """
        Gathers a list of currently running executions by state machine arn.

        Parameters:
            smarn (str) = the arn of the state machine.
        
        Returns:
            list = a list of currently-running executions of the state machine.
        """

        return self.client.list_executions(
            stateMachineArn=smarn,
            statusFilter='RUNNING'
        )

    def get_pipeline_execution_metadata (
        self,
        executionarn: str
    ) -> PipelineExecutionMetadata:
        """
        Gathers high-level metadata about pipeline execution.

        Parameters:
            executionarn (str) = the arn of the state machine execution.
        
        Returns:
            PipelineExecutionMetadata = metadata object about pipeline.
        
        PipelineExecutionMetadata Attributes:
            executionarn (str) = the arn of the execution.
            status (str) = the status of the execution.
            inputval (str) = the starting state input provided to the execution.
            output (str) = the output of the execution terminal state.
            retries (str) = the number of retries that took place.
        """

        response = self.client.describe_execution (
            executionArn=executionarn
        )

        output = ''

        try:
            output = response['output']
        except Exception as e:
            output = ''

        return PipelineExecutionMetadata (
            executionarn=response['executionArn'],
            status=response['status'],
            inputval=response['input'],
            output=output,
            retries=response['ResponseMetadata']['RetryAttempts']
        )

