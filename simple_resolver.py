import dns.resolver
import dns.query
import dns.message
import dns.flags
import dns.rdatatype
from tabulate import tabulate

def resolve_domain(domain):
    # Creating a DNS query message
    query = dns.message.make_query(domain, dns.rdatatype.A)
    
    # Send the query to a DNS server (you can use 8.8.8.8 or any other DNS server)
    response = dns.query.udp(query, '8.8.8.8')

    # Extracting query and response details
    query_info = []
    response_info = []

    # Query Section
    for question in response.question:
        query_info.append([
            question.name.to_text(),
            dns.rdatatype.to_text(question.rdtype)
        ])

    # Response Section
    for answer in response.answer:
        for item in answer.items:
            response_info.append([
                answer.name.to_text(),
                dns.rdatatype.to_text(answer.rdtype),
                item.to_text()
            ])

    # Display query details in a table
    print("\nQuery Details:")
    print(tabulate(query_info, headers=["Name", "Type"], tablefmt="pretty"))

    # Display response details in a table
    print("\nResponse Details:")
    print(tabulate(response_info, headers=["Name", "Type", "Value"], tablefmt="pretty"))

if __name__ == "__main__":
    domain = input("Enter the domain to resolve: ")
    resolve_domain(domain)

