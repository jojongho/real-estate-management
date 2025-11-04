
import csv

# 1. PDF에서 추출한 분양가 정보를 딕셔너리 형태로 구조화
pricing_data = {
    "84A": {
        "default": {
            (5, 5): {"land": 173607000, "building": 316393000, "vat": 0, "total": 490000000, "contract1": 10000000, "contract2": 39000000, "mid": 49000000, "balance": 147000000},
            (6, 9): {"land": 177256000, "building": 323044000, "vat": 0, "total": 500300000, "contract1": 10000000, "contract2": 40030000, "mid": 50030000, "balance": 150090000},
            (10, 19): {"land": 180870000, "building": 329630000, "vat": 0, "total": 510500000, "contract1": 10000000, "contract2": 41050000, "mid": 51050000, "balance": 153150000},
            (20, 25): {"land": 183209000, "building": 333891000, "vat": 0, "total": 517100000, "contract1": 10000000, "contract2": 41710000, "mid": 51710000, "balance": 155130000},
            (26, 99): {"land": 184484000, "building": 336216000, "vat": 0, "total": 520700000, "contract1": 10000000, "contract2": 42070000, "mid": 52070000, "balance": 156210000}
        },
        "105-5": { # 105동 5호 라인
            (5, 5): {"land": 169993000, "building": 309807000, "vat": 0, "total": 479800000, "contract1": 10000000, "contract2": 37980000, "mid": 47980000, "balance": 143940000},
            (6, 9): {"land": 173607000, "building": 316393000, "vat": 0, "total": 490000000, "contract1": 10000000, "contract2": 39000000, "mid": 49000000, "balance": 147000000},
            (10, 19): {"land": 177256000, "building": 323044000, "vat": 0, "total": 500300000, "contract1": 10000000, "contract2": 40030000, "mid": 50030000, "balance": 150090000},
            (20, 25): {"land": 179595000, "building": 327305000, "vat": 0, "total": 506900000, "contract1": 10000000, "contract2": 40690000, "mid": 50690000, "balance": 152070000},
            (26, 99): {"land": 180870000, "building": 329630000, "vat": 0, "total": 510500000, "contract1": 10000000, "contract2": 41050000, "mid": 51050000, "balance": 153150000}
        }
    },
    "84B": {
        "default": {
            (5, 5): {"land": 171198000, "building": 312002000, "vat": 0, "total": 483200000, "contract1": 10000000, "contract2": 38320000, "mid": 48320000, "balance": 144960000},
            (6, 9): {"land": 174776000, "building": 318524000, "vat": 0, "total": 493300000, "contract1": 10000000, "contract2": 39330000, "mid": 49330000, "balance": 147990000},
            (10, 19): {"land": 178390000, "building": 325110000, "vat": 0, "total": 503500000, "contract1": 10000000, "contract2": 40350000, "mid": 50350000, "balance": 151050000},
            (20, 25): {"land": 180728000, "building": 329372000, "vat": 0, "total": 510100000, "contract1": 10000000, "contract2": 41010000, "mid": 51010000, "balance": 153030000},
            (26, 99): {"land": 182004000, "building": 331696000, "vat": 0, "total": 513700000, "contract1": 10000000, "contract2": 41370000, "mid": 51370000, "balance": 154110000}
        }
    },
    "84T": {
        "default": {
            (1, 1): {"land": 187141000, "building": 341059000, "vat": 0, "total": 528200000, "contract1": 10000000, "contract2": 42820000, "mid": 52820000, "balance": 158460000},
            (2, 2): {"land": 191641000, "building": 349259000, "vat": 0, "total": 540900000, "contract1": 10000000, "contract2": 44090000, "mid": 54090000, "balance": 162270000}
        }
    },
    "99A": {
        "default": {
            (1, 1): {"land": 195007000, "building": 323084550, "vat": 32308450, "total": 550400000, "contract1": 10000000, "contract2": 45040000, "mid": 55040000, "balance": 165120000},
            (2, 2): {"land": 200321000, "building": 331890000, "vat": 33189000, "total": 565400000, "contract1": 10000000, "contract2": 46540000, "mid": 56540000, "balance": 169620000},
            (3, 3): {"land": 204608000, "building": 338992730, "vat": 33899270, "total": 577500000, "contract1": 10000000, "contract2": 47750000, "mid": 57750000, "balance": 173250000},
            (4, 4): {"land": 208895000, "building": 346095450, "vat": 34609550, "total": 589600000, "contract1": 10000000, "contract2": 48960000, "mid": 58960000, "balance": 176880000},
            (5, 5): {"land": 212084000, "building": 351378180, "vat": 35137820, "total": 598600000, "contract1": 10000000, "contract2": 49860000, "mid": 59860000, "balance": 179580000},
            (6, 9): {"land": 216371000, "building": 358480910, "vat": 35848090, "total": 610700000, "contract1": 10000000, "contract2": 51070000, "mid": 61070000, "balance": 183210000},
            (10, 19): {"land": 220658000, "building": 365583640, "vat": 36558360, "total": 622800000, "contract1": 10000000, "contract2": 52280000, "mid": 62280000, "balance": 186840000},
            (20, 25): {"land": 223422000, "building": 370161820, "vat": 37016180, "total": 630600000, "contract1": 10000000, "contract2": 53060000, "mid": 63060000, "balance": 189180000},
            (26, 99): {"land": 224910000, "building": 372627270, "vat": 37262730, "total": 634800000, "contract1": 10000000, "contract2": 53480000, "mid": 63480000, "balance": 190440000}
        },
        "104-1": { # 104동 1호 라인
            (1, 1): {"land": 190720000, "building": 315981820, "vat": 31598180, "total": 538300000, "contract1": 10000000, "contract2": 43830000, "mid": 53830000, "balance": 161490000},
            (2, 2): {"land": 196070000, "building": 324845450, "vat": 32484550, "total": 553400000, "contract1": 10000000, "contract2": 45340000, "mid": 55340000, "balance": 166020000},
            (3, 3): {"land": 200321000, "building": 331890000, "vat": 33189000, "total": 565400000, "contract1": 10000000, "contract2": 46540000, "mid": 56540000, "balance": 169620000},
            (4, 4): {"land": 204608000, "building": 338992730, "vat": 33899270, "total": 577500000, "contract1": 10000000, "contract2": 47750000, "mid": 57750000, "balance": 173250000},
            (5, 5): {"land": 207832000, "building": 344334550, "vat": 34433450, "total": 586600000, "contract1": 10000000, "contract2": 48660000, "mid": 58660000, "balance": 175980000},
            (6, 9): {"land": 212084000, "building": 351378180, "vat": 35137820, "total": 598600000, "contract1": 10000000, "contract2": 49860000, "mid": 59860000, "balance": 179580000},
            (10, 19): {"land": 216371000, "building": 358480910, "vat": 35848090, "total": 610700000, "contract1": 10000000, "contract2": 51070000, "mid": 61070000, "balance": 183210000},
            (20, 25): {"land": 219135000, "building": 363059090, "vat": 36305910, "total": 618500000, "contract1": 10000000, "contract2": 51850000, "mid": 61850000, "balance": 185550000},
            (26, 99): {"land": 220658000, "building": 365583640, "vat": 36558360, "total": 622800000, "contract1": 10000000, "contract2": 52280000, "mid": 62280000, "balance": 186840000}
        }
    },
    "99B": {
        "default": {
            (2, 2): {"land": 199081000, "building": 329835450, "vat": 32983550, "total": 561900000, "contract1": 10000000, "contract2": 46190000, "mid": 56190000, "balance": 168570000},
            (3, 3): {"land": 203333000, "building": 336879090, "vat": 33687910, "total": 573900000, "contract1": 10000000, "contract2": 47390000, "mid": 57390000, "balance": 172170000},
            (4, 4): {"land": 207584000, "building": 343923640, "vat": 34392360, "total": 585900000, "contract1": 10000000, "contract2": 48590000, "mid": 58590000, "balance": 175770000},
            (5, 5): {"land": 210809000, "building": 349264550, "vat": 34926450, "total": 595000000, "contract1": 10000000, "contract2": 49500000, "mid": 59500000, "balance": 178500000},
            (6, 9): {"land": 215060000, "building": 356309090, "vat": 35630910, "total": 607000000, "contract1": 10000000, "contract2": 50700000, "mid": 60700000, "balance": 182100000},
            (10, 19): {"land": 219347000, "building": 363411820, "vat": 36341180, "total": 619100000, "contract1": 10000000, "contract2": 51910000, "mid": 61910000, "balance": 185730000},
            (20, 25): {"land": 222111000, "building": 367990000, "vat": 36799000, "total": 626900000, "contract1": 10000000, "contract2": 52690000, "mid": 62690000, "balance": 188070000},
            (26, 99): {"land": 223599000, "building": 370455450, "vat": 37045550, "total": 631100000, "contract1": 10000000, "contract2": 53110000, "mid": 63110000, "balance": 189330000}
        }
    },
    "150P": {
        "default": {
            (28, 28): {"land": 387781000, "building": 642471820, "vat": 64247180, "total": 1094500000, "contract1": 10000000, "contract2": 99450000, "mid": 109450000, "balance": 328350000}
        }
    },
    "152P": {
        "105-4": {
            (28, 28): {"land": 361953000, "building": 599679090, "vat": 59967910, "total": 1021600000, "contract1": 10000000, "contract2": 92160000, "mid": 102160000, "balance": 306480000}
        },
        "104-3": {
            (22, 22): {"land": 386541000, "building": 640417270, "vat": 64041730, "total": 1091000000, "contract1": 10000000, "contract2": 99100000, "mid": 109100000, "balance": 327300000}
        }
    }
}

def get_price_info(apt_type, dong, ho):
    floor = int(str(ho)[:-2])
    
    # 특별 케이스 키 생성 (e.g., "84A_105-5")
    special_key = f"{dong}-{str(ho)[-1]}"
    
    # 1. 가장 구체적인 키 (타입 + 동-호 라인) 확인
    if apt_type in pricing_data and special_key in pricing_data[apt_type]:
        price_table = pricing_data[apt_type][special_key]
    # 2. 타입 기본값 확인
    elif apt_type in pricing_data and "default" in pricing_data[apt_type]:
        price_table = pricing_data[apt_type]["default"]
    # 3. 매칭 실패
    else:
        return None

    for floor_range, info in price_table.items():
        if floor_range[0] <= floor <= floor_range[1]:
            return info
    return None

input_file = "/Users/jojongho/Flow System/- Flow/01. Framing/Project/아파트 입주자 모집공고문 데이터 정규화 및 마이그레이션/아산탕정동일하이빌파크레인/동일 분양가 매핑전.csv"
output_file = "/Users/jojongho/Flow System/- Flow/01. Framing/Project/아파트 입주자 모집공고문 데이터 정규화 및 마이그레이션/아산탕정동일하이빌파크레인/동일 분양가 매핑후.csv"

with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    header = next(reader)
    writer.writerow(header)
    
    for row in reader:
        dong, ho, apt_type = row[0], row[1], row[2]
        
        info = get_price_info(apt_type, dong, ho)
        
        if info:
            new_row = [
                dong, ho, apt_type,
                info["land"], info["building"], info["vat"], info["total"],
                info["contract1"], info["contract2"],
                info["mid"], info["mid"], info["mid"], info["mid"], info["mid"], info["mid"],
                info["balance"]
            ]
            writer.writerow(new_row)
        else:
            # 매칭되는 정보가 없을 경우 원본 행 유지
            writer.writerow(row)

print(f"매핑 완료. 결과가 '{output_file}'에 저장되었습니다.")
