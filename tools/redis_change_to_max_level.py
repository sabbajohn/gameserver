from log import logger
import random
import os
import redis
import socket
import json


while True:

    print("Este script modificará o valor 'spend_total' de todos os jogadores com 'spend_total' igual ou acima" +
            " do necessário para alcancar o level máximo.\nDeseja continuar?\nDigite 'S' para continuar ou 'N' para cancelar")
    res = input().upper()

    if res == "N":
        logger.info("Operação cancelada")
        break
    elif res == "S":
        try:
            # TODO: Implement throw ./webingo/server
            with open("./fb_social_config.json", "r") as cfgfile:
                facebook_config = json.load(cfgfile)
        except:
            logger.error("Não há arquivo fb_social_config.json dentro do diretório /res, favor verificar")
            break
        check_redis = False
        try:
            d = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
            cname = "webingo_{}_{}".format(socket.gethostname(), os.getpid())
            d.client_setname(cname)
            logger.info('[kvdb] connected to persistency db as {}'.format(cname))
            check_redis = True
        except:
            logger.error("Redis não está rodando ou não está instalado, favor verificar.")
            break

        if check_redis:
            key_list = d.keys("*_DATA")
            modified_list = []
            temp_variable_spend = facebook_config["CRE"]["level_params"]["level_spend_table"][-1][1] * 10
            for key in key_list:
                temp_variable = json.loads(d.get(key))
                try:
                    if temp_variable["spend_total"] > temp_variable_spend:
                        temp_variable["spend_total"] = temp_variable_spend
                        d.set(key, json.dumps(temp_variable))
                        logger.info(f"{key} has been changed. Its spend_total has been changed to {temp_variable['spend_total']}")
                        modified_list.append(key)
                except:
                    pass
            if modified_list == []:
                logger.info("Nenhum player foi modificado")
            print("Você deseja continuar?" +
                    "\nPressione 'S' para continuar ou qualquer outra tecla para sair")
            stayson = input().upper()
            if stayson == "S":
                pass
            else:
                break
            
    else:
        logger.warning("Você digitou letras diferentes de S e N, tente novamente.")
