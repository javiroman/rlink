// File DBConnector.ice
#ifndef _RLINK_ICE
#define _RLINK_ICE

#include <Ice/Identity.ice>

module DBConnector
{
    interface DBInsertion
    {
        void pingTest(string s);
        void linkerToDBConnector(string linkingFolder, string target, string linkerOut, string port);
    };
};
#endif _RLINK_ICE
