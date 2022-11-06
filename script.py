## -- ## -- ## SCRIP BY 0c3x ## -- ## -- ##
# https://github.com/0c3x
## -- ## -- #### -- ## -- #### -- ## -- ##
# -INSTALAÇÕES DOS PACOTES:
#  python -m pip install wmi && python -m pip install mysql-connector-python
#  
## -- ## -- #### -- ## -- #### -- ## -- ##

parametros = dict(
	host="IP DO SERVIDOR",
    user="USUARIO DO MSQL",
    passwd="SENHA DO MSQL",
    database="DATABASE",
    auth_plugin="mysql_native_password"
)

import json
import wmi
import mysql.connector
from mysql.connector.errors import ProgrammingError
from time import sleep
import os, sys


proc = wmi.WMI()




with open('config.json') as f:
    dados = json.load(f)

    # NOME DO EXECUTAVEL
    executavel = dados["executavel"]
    # NOME DO ROBO (30)
    robo = dados["robo"]
    # TIPO DE SERVICO (30)
    tipo = dados["tipo"]

    del dados


# MAC ADDRESS (17)
for interface in proc.Win32_NetworkAdapterConfiguration(IPEnabled=1):
    mac = interface.MACAddress


########    #########    ##########   ##########   ########  ###
# FUNCAO RESPONSAVEL POR VERIFICAR STATUS ATUAL DO EXECUTAVEL
########    #########    ##########   ##########   ######## ####
def statusSystem():
    status = False
    for process in proc.Win32_Process():
        if executavel in process.Name:
            status = True
    if status:
        return 1
    else:
        return 0

#######################
# [+] PRIMEIRO ACESSO #
#######################

try:
    # ESTABELECIMENTO DA CONEXAO COM O BANCO DE DADOS
    con = mysql.connector.connect(**parametros)

    # VERIFICACAO SE A MAQUINA FOI CADASTRADA ANTERIORMENTE PELO MAC
    try:
        query = f"SELECT IDROBO FROM MONITORA_ROBO WHERE MAC='{mac}'"    
        cursor = con.cursor()
        cursor.execute(query)
        machine_db = cursor.fetchone()

        # FECHAMENTO DE CONEXAO COM DB
        con.close()
        del con
    except ProgrammingError as e:
        print(f"erro no banco de dados: {e.msg}")
except:
    print("Erro ao se Conectar ao Banco de Dados")


if not machine_db:
    try:
        # ESTABELECIMENTO DA CONEXAO COM O BANCO DE DADOS
        con = mysql.connector.connect(**parametros)

        # CONSULTA DO IPv4 DO SERVIDOR PRINCIPAL
        situacao = statusSystem()
        query = f"SELECT host FROM information_schema.processlist "
        query += f"WHERE id = connection_id( ) LIMIT 1"
        stmt = con.cursor()
        stmt.execute(query)
        t = stmt.fetchone()
        ip = t[0].split(":")[0]

        # PRIMEIRA ATUALIZACAO DE STATUS / NOVO CADASTRO
        query = f"INSERT INTO MONITORA_ROBO(IDROBO, MAC, status, ULTIMA_ATT, ULTIMA_MUD, ROBO, IPSERVIDOR, TIPO_SERVICO) values(NULL ,'{mac}',{situacao}, (SELECT NOW()), (SELECT NOW()), '{robo}', '{ip}', '{tipo}');"    
        con.cursor().execute(query)
        con.commit()

        # FECHAMENTO DE CONEXAO COM DB
        con.close()
        del con

        # WAIT HALF-SECOND
        sleep(0.5)
    except ProgrammingError as e:
        print(f"erro no banco de dados: {e.msg}")






##########################
#  ATUALIZACAO DE STATUS #
#    (MONITORAMENTO)     #
##########################

# # # # LOOP INFINITO # # # # 
# # # # # # # # # # # # # # # 
while True:
    # VERIFICACAO DE STATUS
    situacao = statusSystem()

## -- ## -- ## ATIVIDADE ## -- ## -- ##
            # GET DO ULTIMO STATUS #
    try:
        # ESTABELECIMENTO DA CONEXAO COM O BANCO DE DADOS
        con = mysql.connector.connect(**parametros)

        queryStatus = f"SELECT STATUS FROM MONITORA_ROBO WHERE MAC='{mac}'"
        stmt = con.cursor()
        stmt.execute(queryStatus)
        statusOld = stmt.fetchone()

        # FECHAMENTO DE CONEXAO COM DB
        con.close()
        del con

    except ProgrammingError as e:
        print(f"erro no banco de dados: {e.msg}")

## -- ## -- ## ATIVIDADE ## -- ## -- ##
            # ATUALIZACAO DE REGISTRO#
    try:
        # ESTABELECIMENTO DA CONEXAO COM O BANCO DE DADOS
        con = mysql.connector.connect(**parametros)

        queryUpdate = f"UPDATE MONITORA_ROBO SET STATUS='{situacao}', ULTIMA_ATT=(SELECT NOW()) WHERE mac='{mac}'"
        con.cursor().execute(queryUpdate)
        con.commit()

        # FECHAMENTO DE CONEXAO COM DB
        con.close()
        del con

    except ProgrammingError as e:
        print(f"erro no banco de dados: {e.msg}")

## -- ## -- ## ATIVIDADE ## -- ## -- ##
            # GET NOVO STATUS #
    
    try:
        # ESTABELECIMENTO DA CONEXAO COM O BANCO DE DADOS
        con = mysql.connector.connect(**parametros)

        queryStatus = f"SELECT STATUS FROM MONITORA_ROBO WHERE MAC='{mac}'"
        stmt = con.cursor()
        stmt.execute(queryStatus)
        statusNew = stmt.fetchone()

        # FECHAMENTO DE CONEXAO COM DB
        con.close()
        del con

    except ProgrammingError as e:
        print(f"erro no banco de dados: {e.msg}")

## -- ## -- ## ATIVIDADE ## -- ## -- ##
            # SET ULTIMA MUDANCA #
    # ESTABELECIMENTO DA CONEXAO COM O BANCO DE DADOS
    con = mysql.connector.connect(**parametros)
    if statusOld != statusNew:
        queryAtt = f"UPDATE MONITORA_ROBO SET ULTIMA_MUD=(SELECT NOW()) AND RST=(RST+1) WHERE MAC='{mac}'"
        stmt = con.cursor()
        stmt.execute(queryAtt)
        con.commit()
    
    # FECHAMENTO DE CONEXAO COM DB
    con.close()
    del con

    ## -- ## -- ## ESPERA DE 15 SEGUNDOS PARA VERIFICAR NOVAMENTE ## -- ## -- ##
    sleep(15)




