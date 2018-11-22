import sys
import getopt
import time
import copy
import threading
import random


mutex = threading.Lock()
generals = []
orderKey = ''
COMMAND = {'a': 'Attack', 'r': 'Retreat'}
inputCmd = COMMAND['a']

def getOppositeCmd(cmd):
    if cmd == COMMAND['a']: return COMMAND['r']
    if cmd == COMMAND['r']: return COMMAND['a']

        		   
class general(threading.Thread):
    # default generals in total is 7
    # default traitors are 2
    n = 7
    m = 2
	   
    def __init__(self,iscommander,istraitor,id) :
        threading.Thread.__init__(self)
        self.commander = iscommander
        self.traitor = istraitor
        self.ID = id
        self.messages = []
        self.message_waitlist = []
        self.mutex = threading.Lock()
    
    def run(self) :
        if mutex.acquire():
            print "[general %d] %s" % (self.ID, 'commander: %s, traitor: %s' % (str(self.commander),str(self.traitor)))
            mutex.release()

        time.sleep(0.2)

        if self.commander :
            self.send_command_to_general(":%s" % (inputCmd))
        else :
            # this num represents the total number of messages that this general should send+receive
            diff_arr = [[general.n - 2 - j for j in range(0, i+1)] for i in range(0, general.m)]
            product_arr = [reduce(lambda x,y: x*y, i) for i in diff_arr]
            total_msg_num = reduce(lambda x,y: x+y, product_arr) + 1

            while total_msg_num > len(self.messages):
                msg = self.receive()
                self.messages.append(msg)
                self.send_command_to_general(msg)

            for m in self.messages :
                path, msg = m.split(':')
                path, msg = (map(int,path.split('==>>')), msg)

                if len(path) == 1 :
                    result = self.vote(path,msg,general.m)
                    break
            
            if mutex.acquire():
                print "[general %d] %s" % (self.ID, "The voted final command is: " + str(result))
                mutex.release()
    
    def get_msg(self,path) :
        path = "==>>".join(map(str,path))
        
        for message in self.messages:
            temp_path, msg = message.split(':')
            if temp_path == path :
                return msg
                            
    def vote(self,path,msg,m):
        
        results = [msg]

        # the remaining generals
        generals = [ x for x in range(0,general.n) if x not in path and x != self.ID]

        if m == 0:
            return self.get_msg(path)
        else:
            for g in generals :
                tmp_path = copy.copy(path)
                tmp_path.append(g)
                msg = self.get_msg(tmp_path)
                
                result = self.vote(tmp_path,msg,m-1)
                results.append(result)
                    
            # if the order is tie, then randomly select one from them
            if results.count(inputCmd) > len(results)/2 : 
                return inputCmd
            elif results.count(inputCmd) == len(results)/2: 
                if random.randint(0,1) == 0:
                    return inputCmd
                return getOppositeCmd(inputCmd)
            else: 
                return getOppositeCmd(inputCmd)
            
    def send_command_to_general(self,msg) :
        path,cmd = msg.split(":")
        
        if path=='':
            path = [self.ID]
        else:
            path = map(int,path.split('==>>'))
            path.append(self.ID)
        
        if len(path) == general.m + 2 : return False

        for g in generals :
            if g.ID not in path :
                msg = '==>>'.join(map(str,path))
                oppositeCmd = getOppositeCmd(inputCmd)
                cmd = oppositeCmd if (self.traitor and g.ID % 2 == 0 and not self.commander) else inputCmd
                self.send(g,msg+':'+cmd)
        return True
    
    def send(self,g,msg):
        if mutex.acquire():
            print "[general %d] %s" % (self.ID, 'Send to %d, and the message is: ' % (g.ID) + msg)
            mutex.release()
        
        if g.mutex.acquire():
            g.message_waitlist.append(msg)
            g.mutex.release()
                    
    def receive(self) :
        msg = ''
        while msg is '':
            if self.mutex.acquire():
                if(len(self.message_waitlist) > 0):
                    msg = self.message_waitlist.pop(0)
                self.mutex.release()
        
        return msg
					   
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "m:n:o:a:r:")
    except getopt.error, msg:
        print "Usage: python byzantine.py -n [num of generals] -m [num of traitor] -o [the order should either 'a' or 'r']"
        sys.exit(-1)
    
    for option, value in opts:
        if option == "-m":
            general.m = int(value)
        if option == "-n":
            general.n = int(value)
        if option == "-o":
            orderKey = str(value)

    inputCmd = COMMAND[orderKey]
    
    print 'N is %d; M is %d; Order is %s' % (general.n, general.m, inputCmd)

    # initialized the number of traitors
    m = 0

    for i in xrange(general.n) :
        iscommander = True if 0 == i else False
        if m >= general.m :
            istraitor = False
        else :
            istraitor = True if random.randint(0,1) == 0 else False
            if istraitor :
                m += 1
            if i == general.n - 1 and m < general.m:
                istraitor = True
        
        g = general(iscommander,istraitor,i)
        generals.append(g)
        g.start()
    
    for g in generals :
        g.join()