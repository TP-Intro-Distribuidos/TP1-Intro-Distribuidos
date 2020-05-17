import dns.resolver
from flask import make_response, jsonify
import datetime
from itertools import cycle

# Data to serve with our API
custom_domains = [
    {
        "custom": "true",
        "domain": "a.b.c",
        "ip": "192.33.22.11"
    }
]

cached_domains = {}


class DomainInformation:

    def __init__(self, ips, ttl):
        self.iterator = cycle(ips)
        self.expiration = datetime.datetime.now() + datetime.timedelta(seconds=ttl)

    def is_still_valid(self):
        return self.expiration > datetime.datetime.now()

    def get_next_ip(self):
        return next(self.iterator)


# Provided examples separator
def get_domain(domain):
    """
    Obtiene la IP asociada a un dominio en particular, pudiendo ser este un custom domain
    creado previamente. Si en hostname tiene varias IPs distintas, el servicio deberá devolver
    sólo una. Sin embargo, si se vuelve a pedir la IP de ese dominio, deberá irse alternando
    entre las que provee el resolver de DNS en forma de round robin.
    :param domain:  El dominio que se quiere consultar
    :return:    200 dominio, 404 dominio no encontrado.
    """

    # First we search in our local list of custom domains
    localList = list(filter(lambda d: d.get('domain') == domain, custom_domains))
    if len(localList) > 0:
        return localList[0]

    # If not, we search in our cache
    if domain in cached_domains:
        domain_info = cached_domains[domain]
        if domain_info.is_still_valid():
            return make_response(format_answer(domain, domain_info.get_next_ip()), 200)

    # If not, we get the list from the real DNS resolver
    try:
        result = dns.resolver.query(domain)
        if (len(result)) > 0:
            list_of_ips = []
            for res in result:
                print(res.to_text())
                list_of_ips.append(res.to_text())
            cached_domains[domain] = DomainInformation(list_of_ips, result.ttl)
            return make_response(format_answer(domain, cached_domains[domain].get_next_ip()), 200)
    except:
        return make_response({'error': 'domain not found'}, 404)

    return make_response({'error': 'domain not found'}, 404)


def format_answer(domain, ip):
    return {
        "custom": "false",
        "domain": domain,
        "ip": str(ip)
    }


def get_custom_domains(**kwargs):
    """
    Devuelve el listado de dominios existentes que matcheen con el string provisto.
    :return:    200 custom domains que matcheen con la query o vacio.
    """
    query = kwargs.get('q')
    if query is None:
        return custom_domains

    return jsonify(items=list(filter(lambda d: str(query) in d.get('domain'), custom_domains)))


def modify_existent_domain(domain, **kwargs):
    """
    Esta funcion maneja el request PUT /api/custom-domains/{domain}

    """

    new_domain = kwargs.get('body')
    domain_body = new_domain.get('domain')
    ip = new_domain.get('ip')

    if not domain_body or not ip:
        return make_response({'error': 'payload is invalid'}, 400)

    dup = False
    for existent_domain in custom_domains:
        dup = domain == existent_domain.get('domain')
        if dup:
            existent_domain["ip"] = ip
            return make_response(existent_domain, 200)

    if not dup:
        return make_response({'error': 'domain not found'}, 404)


def create_custom_domain(**kwargs):
    """
    Esta funcion maneja el request POST /api/custom-domains

    """
    new_domain = kwargs.get('body')
    domain = new_domain.get('domain')
    ip = new_domain.get('ip')

    if not domain or not ip:
        return make_response({'error': 'custom domain already exists'}, 400)

    dup = False
    for existent_domain in custom_domains:
        dup = domain == existent_domain.get('domain')
        if dup: break

    if dup:
        return make_response({'error': 'custom domain already exists'}, 400)

    new_domain = {
        'domain': domain,
        'ip': ip,
        'custom': True
    }

    custom_domains.append(new_domain)

    return make_response(new_domain, 201)


def delete_custom_domain(domain):
    """
    Esta funcion maneja el request DELETE /api/custom-domains/{domain}

    """

    dup = False
    for existent_domain in custom_domains:
        dup = domain == existent_domain.get('domain')
        if dup:
            custom_domains.remove(existent_domain)
            break

    if not dup:
        return make_response({'error': 'domain not found'}, 404)

    domain_response = {
        'domain': domain
    }

    return make_response(domain_response, 200)
