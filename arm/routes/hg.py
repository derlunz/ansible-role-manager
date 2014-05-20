import re, os
import hgapi
from . import Route, ROUTE_REGEX
from arm import Role
from arm.util import fetch_git_repository
from yaml import load, Loader

class BaseRoute(Route):
        
    '''
    
    #### pip-style patterns
    hg+http://git.myproject.org/MyProject
    hg+ssh://git@myproject.org/MyProject
    
    #### all support
    @branch
    @commit (hexidecimal)
    @tag

    '''

    patterns = [

        re.compile(r'^hg\+(?P<protocol>http[s]{0,1}):\/\/%(fqdn)s\/%(owner)s\/%(repo)s%(tag)s' % ROUTE_REGEX),
        re.compile(r'^hg\+(?P<protocol>ssh)\:\/\/(%(user)s\@){0,1}%(fqdn)s\/%(owner)s\/%(repo)s%(tag)s' % ROUTE_REGEX),

        ]
    
    def __init__(self):
        pass
    
    def is_valid(self, identifier):
        matches = [True for p in self.patterns if p.match(identifier)] 
        return len(matches) != 0
    
    
    def fetch(self, identifier):
        print "\nFetching `%s` from mercurial..." % identifier
        matches = [p.match(identifier).groupdict() for p in self.patterns if p.match(identifier)]
        
        info = matches[0]
        
        params = {
            'root':get_playbook_root(os.getcwd()),
            'server':info['fqdn'],
            'owner':info['owner'],
            'repo':info['repo'],
        }
        
        if info.get('tag', None):
            params['tag'] = info['tag']
            
        if info.get('user', None):
            params['user'] = info['user']
            
        if info.get('protocol', None):
            params['protocol'] = info['protocol']
            
        _source = "%s://%s/%s/%s" % (protocol, server, owner, repo)
        _destination = '%(root)s/.cache/%(repo)s' % params
    
        repo = hgapi.hg_clone(_source, _destination)
        
        meta_path = os.path.join(location, 'meta/main.yml')
        if os.path.exists(meta_path):
            meta_info = load(open(meta_path, 'r'), Loader=Loader)
            meta_info.update({ 'github_user':info['owner'],'github_repo':info['repo']})
            
            return Role(location, **meta_info)
        
        print "WARNING : The role '%s' does not have a meta/main.yml. Role attributes & dependencies not available."
        return Role(location,{
            'github_user':info['owner'],
            'github_repo':info['repo']
        })
            
            
        
        
                                          
    
    
    