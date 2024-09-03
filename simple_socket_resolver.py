import struct
import socket
from tabulate import tabulate

def build_dns_query(domain, query_type):
    # Transaction ID (2 bytes)
    transaction_id = 0x1234
    flags = 0x0100  # Standard query, recursion desired
    questions = 1  # One question
    answer_rrs = 0  # No answers
    authority_rrs = 0
    additional_rrs = 0

    # DNS Header (12 bytes)
    header = struct.pack('>HHHHHH', transaction_id, flags, questions, answer_rrs, authority_rrs, additional_rrs)

    # Question section
    qname = b''.join(struct.pack('>B', len(part)) + part.encode('utf-8') for part in domain.split('.')) + b'\x00'
    qclass = 1  # Class IN (Internet)

    # Pack the query type (A = 1, MX = 15)
    question = struct.pack('>HH', query_type, qclass)

    return header + qname + question, transaction_id

def parse_dns_response(response, query_type):
    # Parse DNS Header
    header = struct.unpack('>HHHHHH', response[:12])
    transaction_id, flags, questions, answer_rrs, authority_rrs, additional_rrs = header

    flags_details = {
        'QR': (flags >> 15) & 1,  # Query/Response Flag
        'Opcode': (flags >> 11) & 0xF,  # Operation Code
        'AA': (flags >> 10) & 1,  # Authoritative Answer
        'TC': (flags >> 9) & 1,  # Truncated
        'RD': (flags >> 8) & 1,  # Recursion Desired
        'RA': (flags >> 7) & 1,  # Recursion Available
        'Z': (flags >> 6) & 1,  # Reserved
        'AD': (flags >> 5) & 1,  # Authenticated Data
        'CD': (flags >> 4) & 1,  # Checking Disabled
        'Rcode': flags & 0xF  # Response Code
    }

    # Parse the Question section
    offset = 12
    questions_list = []
    for _ in range(questions):
        qname = []
        while True:
            length = response[offset]
            if length == 0:
                offset += 1
                break
            qname.append(response[offset + 1:offset + 1 + length].decode('utf-8'))
            offset += length + 1
        qtype, qclass = struct.unpack('>HH', response[offset:offset + 4])
        offset += 4
        questions_list.append(('.'.join(qname), qtype, qclass))

    # Parse the Answer section
    answers_list = []
    for _ in range(answer_rrs):
        aname = response[offset:offset + 2]
        atype, aclass, ttl, rdlength = struct.unpack('>HHIH', response[offset + 2:offset + 12])
        rdata = response[offset + 12:offset + 12 + rdlength]
        
        if atype == 1:  # A record
            ip = socket.inet_ntoa(rdata)
            answers_list.append((atype, aclass, ttl, ip))
        elif atype == 15:  # MX record
            preference = struct.unpack('>H', rdata[:2])[0]
            exchange = []
            rd_offset = 2
            while rd_offset < len(rdata):
                length = rdata[rd_offset]
                if length == 0:
                    break
                exchange.append(rdata[rd_offset + 1:rd_offset + 1 + length].decode('utf-8'))
                rd_offset += length + 1
            answers_list.append((atype, aclass, ttl, preference, '.'.join(exchange)))

        offset += 12 + rdlength

    return header, flags_details, questions_list, answers_list

def display_dns_details(header, flags, questions, answers, query_type):
    # Display DNS Header
    header_table = [
        ['Transaction ID', hex(header[0])],
        ['Flags', bin(header[1])],
        ['Questions', header[2]],
        ['Answer RRs', header[3]],
        ['Authority RRs', header[4]],
        ['Additional RRs', header[5]]
    ]
    print("\nDNS Header:")
    print(tabulate(header_table, headers=["Field", "Value"], tablefmt="pretty"))

    # Display Flags
    flags_table = [[k, v] for k, v in flags.items()]
    print("\nFlags:")
    print(tabulate(flags_table, headers=["Flag", "Value"], tablefmt="pretty"))

    # Display Questions
    questions_table = [[qname, qtype, qclass] for qname, qtype, qclass in questions]
    print("\nQuestions:")
    print(tabulate(questions_table, headers=["Name", "Type", "Class"], tablefmt="pretty"))

    # Display Answers
    if answers:
        if query_type == 1:  # A record
            answers_table = [[atype, aclass, ttl, rdata] for atype, aclass, ttl, rdata in answers]
            print("\nAnswers:")
            print(tabulate(answers_table, headers=["Type", "Class", "TTL", "RDATA"], tablefmt="pretty"))
        elif query_type == 15:  # MX record
            answers_table = [[atype, aclass, ttl, preference, exchange] for atype, aclass, ttl, preference, exchange in answers]
            print("\nMX Records:")
            print(tabulate(answers_table, headers=["Type", "Class", "TTL", "Preference", "Exchange"], tablefmt="pretty"))
    else:
        print("\nNo Answers")

def resolve(domain, query_type):
    query, transaction_id = build_dns_query(domain, query_type)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    server_address = ('8.8.8.8', 53)
    sock.sendto(query, server_address)

    try:
        response, _ = sock.recvfrom(512)
        header, flags, questions, answers = parse_dns_response(response, query_type)
        display_dns_details(header, flags, questions, answers, query_type)
    except socket.timeout:
        print("Request timed out.")
    finally:
        sock.close()

if __name__ == "__main__":
    domain = input("Enter the domain to resolve: ")
    record_type = input("Enter the record type (A or MX): ").strip().upper()
    if record_type == "A":
        query_type = 1  # A record
    elif record_type == "MX":
        query_type = 15  # MX record
    else:
        print("Unsupported record type.")
        exit(1)

    resolve(domain, query_type)

