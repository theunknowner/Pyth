def get_filename(filename,end=""):
    for i in range(0,len(filename)):
        if(filename[i]=="/"):
            pos = i+1
        if(filename[i]=="."):
            pos2 = i;
       
    name = filename[pos:pos2]
    if(end!=""):
        pos = name.find(end);
        name = name[0:pos];
    return name