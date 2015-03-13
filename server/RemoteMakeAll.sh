#!/bin/bash -xv

LOGFILE=`pwd`/RemoteMakeAll.log

# parametros: $1 : Descripcion
#             $2 : directorio del makefile
#             $3 : makefile
Compile()
{
   echo "procesando $1" >>$LOGFILE

   printf "Compilando: %-30s" "$1"

   pushd . >/dev/null 2>/dev/null

   cd $2 2>>$LOGFILE

   make -f $3 >>$LOGFILE 2>>$LOGFILE

   if [ $? -eq 0 ]; then
      printf "\e[32m [OK] \e[0;37m\n"
   else
      printf "\e[31m [ERROR] \e[0;37m\n"
   fi

   popd >/dev/null 2>/dev/null
}

# parametros: $1 : Descripcion
#             $2 : directorio con el MakeAll.sh
CompileEX()
{
   echo "procesando $1" >>$LOGFILE

   printf "Compilando: %-30s" "$1"

   pushd . >/dev/null 2>/dev/null

   cd $2 2>>$LOGFILE

   ./MakeAll.sh

   if [ $? -eq 0 ]; then
      printf "\e[32m [OK] \e[0;37m\n"
   else
      printf "\e[31m [ERROR] \e[0;37m\n"
   fi

   popd >/dev/null 2>/dev/null
}

> $LOGFILE

Compile   "Server:Quick WINS"             server/QUICK_WINS/obj          Makefile
Compile   "Server:Daemons"                server/daemons                 Makefile
Compile   "Server:Inventario permanente"  server/invenper/obj            Makefile
Compile   "Server:Miscelanea (Makefile)"  server/miscelanea/obj          Makefile
Compile   "Server:Miscelanea (reptest)"   server/miscelanea/obj          reptest.mak
Compile   "Server:Reparto"                server/reparto/obj             Makefile
Compile   "Server:Seguridad"              server/seguridad/obj           Makefile
Compile   "Server:Promocional"            server/spromo/obj              Makefile
Compile   "Server:Tesoreria"              server/tesoreria/obj           Makefile
Compile   "POS:   Programa de caja"       pos                            Makefile

