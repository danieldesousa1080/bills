#!/bin/bash

echo "Olá! Este programa te ajudará a restaurar um banco de dados mongo em formato .dump"

echo "Insira o nome do container docker: "
read container_name
echo "Possui autenticação?  [S/n]"
read has_auth

if [[ $has_auth != "n" ]] && [[ $has_auth != "N" ]]; then
  echo "Digite o nome de usuario: "
  read username
  echo "Digite a senha: "
  read password
fi

echo "Digite o nome do arquivo de backup: "
read filename

if [[ $has_auth != "n" ]] && [[ $has_auth != "N" ]]; then
  docker exec -i $container_name /usr/bin/mongorestore --username $username --password $password --authenticationDatabase admin --nsInclude="*" --archive <"$filename"
else
  docker exec -i $container_name /usr/bin/mongorestore --nsInclude="*" --archive <$filename
fi
