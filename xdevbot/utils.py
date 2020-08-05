import yaml
from aiohttp import ClientSession, ClientTimeout


def repo_fullname_from_url(url: str) -> str:
    return '/'.join(url.split('/')[-2:])


def refs_from_note(note: str) -> str:
    refs = set()
    for word in note.split():
        s = word.split('/')
        if (
            len(s) == 7
            and s[0] in ('http:', 'https:')
            and s[1] == ''
            and s[2] == 'github.com'
            and s[5] in ('issues', 'pull')
        ):
            try:
                int(s[6])
            except ValueError:
                continue
            else:
                refs.add(word)
    return list(refs)


async def get_rate_limits(token: str = None, timeout: int = 60) -> dict:
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'token {token}'
    timeout = ClientTimeout(total=timeout)
    async with ClientSession(headers=headers, timeout=timeout) as session:
        response = await session.get('https://api.github.com/rate_limit')
    if response.status == 200:
        rates = await response.json()
        return rates['resources']
    else:
        return None


async def read_remote_yaml(url, timeout=60):
    timeout = ClientTimeout(total=timeout)
    async with ClientSession(timeout=timeout) as session:
        response = await session.get(url)
    if response.status != 200:
        raise RuntimeError(f'Failed to read config file: {response.status}')
    text = await response.text()
    return yaml.safe_load(text)