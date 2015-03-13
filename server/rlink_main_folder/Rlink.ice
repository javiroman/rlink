// File Rlink.ice
#ifndef _RLINK_ICE
#define _RLINK_ICE

#include <Ice/Identity.ice>

module Rlink 
{
    sequence<byte> ByteSeq;

    interface FileTransfer
    {
        void pingTest(string s);
        ByteSeq getFile(string name);
        void sendFile(string name, ByteSeq bytes);
        void uncompress(string name);
	string makeLinking(string name, string target);
	void getOutputs(string name);
	void addClient(Ice::Identity ident);
    };

    interface CallbackFunctions
    {
        void backOutputs(string home, string name, ByteSeq bytes);
    };
};
#endif _RLINK_ICE
