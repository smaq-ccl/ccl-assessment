FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY data_ingester_lambda.py ${LAMBDA_TASK_ROOT}

CMD [ "data_ingester_lambda.lambda_handler" ]
