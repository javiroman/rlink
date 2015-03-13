#!/bin/bash

LOGFILE=`pwd`/CleanAll.log

# parametros: $1 : Descripcion
#             $2 : directorio del makefile
#             $3 : makefile
#             S4 : clean command
Clean()
{
   echo "procesando $1" >>$LOGFILE

   printf "Clean: %-30s" "$1"

   pushd . >/dev/null 2>/dev/null

   cd $2 2>>$LOGFILE

   make -f $3 $4 >>$LOGFILE 2>>$LOGFILE

   if [ $? -eq 0 ]; then
      printf "\e[32m [OK] \e[0;37m\n"
   else
      printf "\e[31m [ERROR] \e[0;37m\n"
   fi

   popd >/dev/null 2>/dev/null
}

# parametros: $1 : Descripcion
#             $2 : directorio con la shell CleanAll.sh
CleanEX()
{
   echo "procesando $1" >>$LOGFILE

   printf "Clean: %-30s" "$1"

   pushd . >/dev/null 2>/dev/null

   cd $2 2>>$LOGFILE

   ./CleanAll.sh

   if [ $? -eq 0 ]; then
      printf "\e[32m [OK] \e[0;37m\n"
   else
      printf "\e[31m [ERROR] \e[0;37m\n"
   fi

   popd >/dev/null 2>/dev/null
}

> $LOGFILE

Clean   "Server:Quick WINS"             server/QUICK_WINS/obj          Makefile     clean
Clean   "Server:Daemons"                server/daemons                 Makefile     clean
Clean   "Server:Inventario permanente"  server/invenper/obj            Makefile     clean
Clean   "Server:Miscelanea (Makefile)"  server/miscelanea/obj          Makefile     clean
Clean   "Server:Reparto"                server/reparto/obj             Makefile     clean
Clean   "Server:Seguridad"              server/seguridad/obj           Makefile     clean
Clean   "Server:Promocional"            server/spromo/obj              Makefile     clean
Clean   "Server:Tesoreria"              server/tesoreria/obj           Makefile     clean
#Clean   "POS:   Libreria Promocional"   pos/spromo                     Makefile     clean
#CleanEX "POS:   Libreria Franjas"       pos/franjas
Clean   "POS:   Programa de caja"       pos                            Makefile     cleanall

