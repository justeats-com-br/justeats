#!/usr/bin/env bash

RED="\e[1;31;40m"
GREEN="\e[1;32;40m"
YELLOW="\e[1;33;40m"
RESET="\e[0;37;40m"

echo_red() { echo -e "$RED${*}$RESET"; }

echo_green() { echo -e "$GREEN${*}$RESET"; }

echo_yellow() { echo -e "$YELLOW${*}$RESET"; }

deploy_prod() {
  export ENVIRONMENT=PROD
  ENVIRONMENT=PROD \
    STAGE=PROD \
    AWS_ACCESS_KEY_ID=$PROD_AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY=$PROD_AWS_SECRET_ACCESS_KEY \
    SUBNET_A=$PROD_SUBNET_A \
    SUBNET_B=$PROD_SUBNET_B \
    VPC_ID=$PROD_VPC_ID \
    DB_HOST=$PROD_DB_HOST \
    DB_NAME=$PROD_DB_NAME \
    DB_PASSWORD=$PROD_DB_PASSWORD \
    DB_PORT=$PROD_DB_PORT \
    DB_USER=$PROD_DB_USER \
    RESTAURANT_HUB_CUSTOM_DOMAIN=$PROD_RESTAURANT_HUB_CUSTOM_DOMAIN \
    RESTAURANT_HUB_ACM_CERTIFICATE_ARN=$PROD_RESTAURANT_HUB_ACM_CERTIFICATE_ARN \
    PLACES_API_KEY=$PROD_PLACES_API_KEY \
    make deploy stage=prod

  if [ $? -ne 0 ]; then
    echo_red "ERROR: deploy on PROD FAILED!"
    echo
    return 1
  fi
}

deploy_dev() {
  export ENVIRONMENT=DEV
  ENVIRONMENT=DEV \
    STAGE=DEV \
    AWS_ACCESS_KEY_ID=$DEV_AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY=$DEV_AWS_SECRET_ACCESS_KEY \
    SUBNET_A=$DEV_SUBNET_A \
    SUBNET_B=$DEV_SUBNET_B \
    VPC_ID=$DEV_VPC_ID \
    DB_HOST=$DEV_DB_HOST \
    DB_NAME=$DEV_DB_NAME \
    DB_PASSWORD=$DEV_DB_PASSWORD \
    DB_PORT=$DEV_DB_PORT \
    DB_USER=$DEV_DB_USER \
    RESTAURANT_HUB_CUSTOM_DOMAIN=$DEV_RESTAURANT_HUB_CUSTOM_DOMAIN \
    RESTAURANT_HUB_ACM_CERTIFICATE_ARN=$DEV_RESTAURANT_HUB_ACM_CERTIFICATE_ARN \
    PLACES_API_KEY=$DEV_PLACES_API_KEY \
    make deploy stage=dev

  if [ $? -ne 0 ]; then
    echo_red "ERROR: deploy on DEV FAILED!"
    echo
    return 1
  fi
}

if [ "$CIRCLE_BRANCH" == "main" ]; then
  if deploy_dev; then
    if deploy_prod; then
      exit 0
    fi
  fi
  exit 1
fi
