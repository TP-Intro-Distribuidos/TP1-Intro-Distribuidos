from flask import abort, make_response
import dns.resolver

# Data to serve with our API
custom_domains = [
    {
        "custom": "true",
        "domain": "a.b.c",
        "ip": "192.33.22.11"
    }
]

# Data to serve with our API
alumnos = {
    1: {
        'id': 1,
        'nombre': 'Cosme Fulanito',
        'dni': '11222333',
        'padron': '88999',
    },
}


# Create a handler for our read (GET) people
def obtener_todos():
    """
    Esta funcion maneja el request GET /api/alumnos

    :return:        200 lista ordenada alfabeticamente de alumnos de la materia
    """
    # Create the list of people from our data
    return sorted(alumnos.values(), key=lambda alumno: alumno.get('nombre'))


def obtener_uno(id_alumno):
    """
    Esta funcion maneja el request GET /api/alumnos/{id_alumno}

     :id_alumno body:  id del alumno que se quiere obtener
    :return:        200 alumno, 404 alumno no encontrado
    """
    if id_alumno not in alumnos:
        return abort(404, 'El alumno no fue encontrado')

    return alumnos.get(id_alumno)


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

    # First we search in our local list
    localList = list(filter(lambda d: d.get('domain') == domain, custom_domains))
    if len(localList) > 0:
        return localList[0]

    # If not, we get the list from the real DNS resolver
    try:
        result = dns.resolver.query(domain)
        if (len(result)) > 0:
            return make_response(dns_answer_to_custom_domain(domain, result), 200)
    except:
        return abort(404, 'domain not found')

    return abort(404, 'domain not found')


def dns_answer_to_custom_domain(domain, result):
    # for answer in result.response.answer:
    #     print(answer)
    return {
        "custom": "false",
        "domain": domain,
        "ip": str(result.response.answer[0][0])
    }


def get_custom_domains(**kwargs):
    """
    Devuelve el listado de dominios existentes que matcheen con el string provist.
    :return:    200 custom domains que matcheen con la query o vacio.
    """
    query = kwargs.get('q')
    if query is None:
        return custom_domains

    return list(filter(lambda d: str(query) in d.get('domain'), custom_domains))


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
