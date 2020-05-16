import dns.resolver

# Resolve www.yahoo.com
try:
    result = dns.resolver.query('comida')
    for answer in result.response.answer:
        print(answer)
except:
    print('error')
