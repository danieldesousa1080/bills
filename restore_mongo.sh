#!/bin/bash

echo "Olá! Este programa te ajudará a restaurar um banco de dados mongo em formato .dump"

echo "Insira o nome do container docker: "
read container_name
echo "Digite o nome de usuario: "
read username
echo "Digite a senha: "
read password

echo "Digite o nome do arquivo de backup: "
read filename

  docker exec -i $container_name /usr/bin/mongorestore --username $username --password $password --authenticationDatabase admin --nsInclude="*" --archive <"$filename"
