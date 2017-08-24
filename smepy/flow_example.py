import struct_case as sc
import sme
import reader

def main():
    name, facts = reader.read_meld_file('water_flow.meld')
    water_flow = sc.StructCase(facts, name)
    name, facts = reader.read_meld_file('heat_flow.meld')
    heat_flow = sc.StructCase(facts, name)

    print 'water flow vs heat flow:'
    sme_1 = sme.SME(water_flow, heat_flow)
    gms = sme_1.match()
    for gm in gms:
        print gm
        print gm.score
        print

if __name__ == '__main__':
    main()
    
