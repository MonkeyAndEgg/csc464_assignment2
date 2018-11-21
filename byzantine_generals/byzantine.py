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
    N = 7
    M = 2
	   
    def __init__(self,iscommander,istraitor,id) :
        threading.Thread.__init__(self)
        self.isCommander = iscommander
        self.isTraitor = istraitor
        self.ID = id
        self.messages = []
        self.message_waitlist = []
        self.mutex = threading.Lock()
    
    def run(self) :
        if mutex.acquire():
            print "[general %d] %s" % (self.ID, 'commander: %s, traitor: %s' % (str(self.isCommander),str(self.isTraitor)))
            mutex.release()

        time.sleep(0.2)

        if self.isCommander :
            self.send_command_to_general(":%s" % (inputCmd))
        else :
            ''' msg_num = 1 + (n-2) + (n-2)(n-3) + ... '''
            num = reduce(lambda x,y:x+y,[reduce(lambda x,y:x*y, i) for i in [[general.N-2-m1 for m1 in range(0,m+1)] for m in range(0,general.M)]])+1

            while num > len(self.messages):
                msg = self.receive()
                self.messages.append(msg)
                self.send_command_to_general(msg)

            for m in self.messages :
                path, msg = m.split(':')
                path, msg = (map(int,path.split('->')), msg)

                if len(path) == 1 :
                    result = self.vote(path,msg,general.M)
                    break
            
            if mutex.acquire():
                print "[general %d] %s" % (self.ID, "The voted final command is: " + str(result))
                mutex.release()
    
    def get_msg(self,path) :
        path = "->".join(map(str,path))
        
        for message in self.messages:
            temp_path, msg = message.split(':')
            if temp_path == path :
                return msg
                            
    def vote(self,path,msg,m):
            
        generals = [ x for x in range(0,general.N) if x not in path and x != self.ID]
        
        results = [msg]

        if m == 0:
            return self.get_msg(path)
        else:
            for g in generals :
                tmp_path = copy.copy(path)
                tmp_path.append(g)
                msg = self.get_msg(tmp_path)
                
                result = self.vote(tmp_path,msg,m-1)
                results.append(result)
                    
            if results.count(inputCmd) > len(results)/2 : return inputCmd
            else : return getOppositeCmd(inputCmd)
            
    def send_command_to_general(self,msg) :
        path,cmd = msg.split(":")
        
        if path=='':
            path = [self.ID]
        else:
            path = map(int,path.split('->'))
            path.append(self.ID)
        
        if len(path) == general.M + 2 : return False

        for g in generals :
            if g.ID not in path :
                msg = '->'.join(map(str,path))
                oppositeCmd = getOppositeCmd(inputCmd)
                cmd = oppositeCmd if (self.isTraitor and g.ID % 2 == 0 and not self.isCommander) else inputCmd
                self.send(g,msg+':'+cmd)
        return True
    
    def send(self,g,msg):
        if mutex.acquire():
            print "[general %d] %s" % (self.ID, 'Send to %d: ' % (g.ID) + msg)
            mutex.release()
        
        if g.mutex.acquire():
            g.message_waitlist.append(msg)
            g.mutex.release()
                    
    def receive(self) :
        msg = None
        while msg is None:
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
        if option == "-n":
            general.N = int(value)
        if option == "-m":
            general.M = int(value)
        if option == "-o":
            orderKey = str(value)

    inputCmd = COMMAND[orderKey]
    
    print 'N is %d; M is %d; Order is %s' % (general.N,general.M, inputCmd)
    
    commander = random.randint(0,general.N-1)

    m = 0

    for i in xrange(general.N) :
        iscommander = True if commander == i else False
        if m >= general.M :
            istraitor = False
        else :
            istraitor = True if random.randint(0,1) == 0 else False
            if istraitor :
                m +=1
        
        g = general(iscommander,istraitor,i)
        generals.append(g)
        g.start()
    
    for g in generals :
        g.join()