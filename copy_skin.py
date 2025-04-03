# creation date : 28 July, 2021
#
# Author :    Res Yudikata
# Contact :   yudikata@gmail.com
#
# Description :
#    can be used to copy skinCluster from one object to many objects at once
# How To use :
#    just Run This entire script   
#    select the source object that have skincluster and then shift select the target meshes and  push the button

import maya.cmds as cmds
import maya.cmds as cmds

   
if cmds.window('ResCopySkinweight_tools', exists=True):
    cmds.deleteUI('ResCopySkinweight_tools')
    
cmds.window('ResCopySkinweight_tools', s=True)
cmds.columnLayout(columnAlign='center', rowSpacing=10)

SSU = 'SS'

def CP(*arg):
    driver= cmds.ls(sl=1)
    driven = cmds.ls(sl=1)
    driven.reverse()
    for x in range(len(driven)-1):   
        def ObjSelection():
            objects=cmds.listRelatives(s=True)
            shapeHistory=cmds.listHistory(driver[0],lv=3)        
            SkinClust=cmds.ls(shapeHistory, typ='skinCluster')
            target=driven[x]
            AssignWeight(SkinClust,target)
            return True        
        def AssignWeight(SkinClust,target):        
            shapeHistory=cmds.listHistory(target,lv=3)    
            oldSkinClust=cmds.ls(shapeHistory,typ='skinCluster')
            if oldSkinClust:    
                cmds.delete(oldSkinClust)
            jnt=cmds.skinCluster(SkinClust, weightedInfluence=True, q=True)
            newSkinClust=cmds.skinCluster(jnt,target,toSelectedBones=True,mi=5, dr=4,rui=0)
            cmds.copySkinWeights(ss=SkinClust[0],ds=newSkinClust[0],nm=True, surfaceAssociation='closestPoint')
            #cmds.rename(newSkinClust,SkinClust[0])
            return newSkinClust 
        ObjSelection()

def renameSkin(*arg):
    sel=cmds.ls(type='transform')
    S_suf=cmds.textField( SSU, query =True,text=1  )    
    for o in sel:
        history = cmds.listHistory( o, pdo = True, il = 1 )
        if history != None:
            for x in history:
                if cmds.nodeType( x ) == "skinCluster":
                    nmspce = o.split( ":" )
                    if len(nmspce) > 1:
                        cmds.rename( x, nmspce[1]+S_suf) 
                    else:
                        cmds.rename( x, nmspce[0]+S_suf)  
                            
                        
cmds.text (l='Tools for copy Skin Weight To many Objects')
cmds.separator( w=180, h=5)
cmds.text ( l='Select source and then shift select the targets meshes') 
cmds.button(label='Copy Skin',bgc=[1,1,0.4], command = CP)
cmds.separator( w=180, h=5)

cmds.text ( l='rename skinCluster node on the scene to match the mesh name') 
cmds.text( label='skinCluster_Suffix :' ,align='left')
S_Suffix = cmds.textField('SS')
cmds.textField( S_Suffix, text='_SKN',edit=True,  )
cmds.button(label='Rename skinCluster',bgc=[1,1,0.4], command = renameSkin)

cmds.showWindow()
