from flask import abort, make_response

# Data to serve with our API
custom_domains = []

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

def create_custom_domain(**kwargs):
    """
    Esta funcion maneja el request POST /api/custom-domains

    """
    new_domain = kwargs.get('body')
    domain = new_domain.get('domain')
    ip = new_domain.get('ip')
    if not domain or not ip:
        return abort(400, 'custom domain already exists')

    dup = False
    for existent_domain in custom_domains:
        dup = domain == existent_domain.get('domain')
        if dup: break

    if dup:
        return abort(400, 'custom domain already exists')

    new_domain = {
        'domain': domain,
        'ip': ip,
        'custom': true
    }

    custom_domains.append(new_domain)

    return make_response(new_domain, 201)

def delete_custom_domain(domain):
    """
    Esta funcion maneja el request DELETE /api/custom-domain/{domain}

    """

    if not any(custom_domain.domains == domain for custom_domain in custom_domains):
        return abort(404, 'domain not found')

    del custom_domains[domain]

    domain_response = {
        'domain': domain
    }

    return make_response(domain_response, 204)
