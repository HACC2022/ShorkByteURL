from typing import Any, List, Optional, Set, Tuple
from db_manager import DBManager
from settings import URL_TBL
from url_pair import URLPair

class URLManager:

    capacity: int = int(1e4)

    def __init__(self, db_manager:DBManager) -> None:
        self.db_manager: DBManager = db_manager
    
    def append(self, orig_url: str, short_url: Optional[str]=None, owner_id: int=4, requester_id: int=4) -> Optional[str]:
        # TODO: change append to insert
        short_urls: Set[str] = set([url[0] for url in self.db_manager.select(from_arg=URL_TBL, select_args=['short_url'])])
        if len(short_urls) >= URLManager.capacity: 
            print('Reached Max Capacity')
            return

        url_pair: URLPair = URLPair(
            orig_url=orig_url,
            short_url=short_url
        )
        while url_pair.short_url in short_urls:
            url_pair.regenerate()
        
        self.db_manager.insert(URL_TBL, [owner_id, requester_id, url_pair.short_url, url_pair.orig_url, self.db_manager.get_timestamp(),'new'])
        return url_pair.short_url
    
    def get(self, short_url:str, default_value:str='', status:str='') -> str:
        # gets orig_url
        status_check: dict[str, str] = {'status': status} if status != '' else {}
        sel: List[Tuple[Any]] = self.db_manager.select(from_arg=URL_TBL, select_args=['orig_url'], where_args={**{'short_url':short_url}, **status_check})

        if not sel:
            return default_value
        return sel[0][0]
    
    def find_pair(self, url:str, status:str='') -> Optional[URLPair]:
        status_check: dict[str, str] = {'status': status} if status != '' else {}
        sel: List[Tuple[Any]] = self.db_manager.select(from_arg=URL_TBL, select_args=['orig_url'], where_args={**{'short_url':url}, **status_check})
        if not sel:
            sel: List[Tuple[Any]] = self.db_manager.select(from_arg=URL_TBL, select_args=['short_url'], where_args={**{'orig_url':url}, **status_check})
            if not sel:
                return None
            return URLPair(sel[0][0], url)
        return URLPair(url, sel[0][0])
    
    def update_status(self, url_id:int, status:str) -> None:
        self.db_manager.update(URL_TBL, set_args={
            'status': status
        }, where_args={
            'url_id': url_id
        })
    
    def clear(self) -> None:
        self.db_manager.truncate(URL_TBL)

    def remove(self, url_pair:URLPair) -> None:
        self.db_manager.delete(URL_TBL, {'short_url':url_pair.short_url, 'orig_url':url_pair.orig_url})

def main() -> None:
    url_manager: URLManager = URLManager(DBManager())
    url_manager.append('google.com')
    url_manager.append('example.com')
    url_manager.get('/compress')
    # url_manager.clear()

if __name__ == '__main__':
    main()