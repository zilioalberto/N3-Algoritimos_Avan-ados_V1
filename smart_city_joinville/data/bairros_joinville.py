#!/usr/bin/env python3
"""
Dados oficiais dos bairros de Joinville
Fonte de backup para validação quando a Wikipedia não estiver disponível
"""

# Lista oficial dos bairros de Joinville (baseada em fontes oficiais)
BAIRROS_JOINVILLE = [
    "ADHEMAR GARCIA",
    "AMERICA",
    "ANITA GARIBALDI",
    "ATIRADORES",
    "AVENTUREIRO",
    "BOA VISTA",
    "BOEHMERWALD",
    "BOM REITIRO",
    "BOM RETIRO",
    "BUCAREIN",
    "CENTRO",
    "COMASA",
    "COSTA E SILVA",
    "DONA FRANCISCA",
    "ESPINHEIROS",
    "FÁTIMA",
    "FLORESTA",
    "GLÓRIA",
    "GUANABARA",
    "IRIRIU",
    "ITAUM",
    "ITINGA",
    "JARDIM IRIRIU",
    "JARDIM PARAÍSO",
    "JARDIM SOFIA",
    "JARIVATUBA",
    "JOAO COSTA",
    "MORRO DO MEIO",
    "NOVA BRASÍLIA",
    "PARANAGUAMIRIM",
    "PARQUE GUARANI",
    "PERIMETRO URBANO",
    "PETRÓPOLIS",
    "PIRABEIRABA",
    "PIRABEIRABA CENTRO",
    "PROFIPO",
    "RIO BONITO",
    "SAGUACU",
    "SANTA CATARINA",
    "SANTO ANTONIO",
    "SÃO MARCOS",
    "ULYSSES GUIMARAES",
    "VILA CUBATÃO",
    "VILA NOVA",
    "ZONA IND NORTE",
    "ZONA IND TUPY",
    "ZONA RURAL",
    "NÃO INFORMADO"
]

def get_bairros_oficiais():
    """Retorna a lista oficial dos bairros de Joinville"""
    return BAIRROS_JOINVILLE.copy()

def validar_bairro(nome_bairro):
    """Valida se um nome de bairro está na lista oficial"""
    return nome_bairro.upper() in BAIRROS_JOINVILLE

def comparar_listas(lista_banco, lista_externa):
    """Compara duas listas de bairros e retorna diferenças"""
    banco_set = set(nome.upper() for nome in lista_banco)
    externa_set = set(nome.upper() for nome in lista_externa)
    
    so_no_banco = banco_set - externa_set
    so_na_externa = externa_set - banco_set
    em_comum = banco_set & externa_set
    
    return {
        'so_no_banco': sorted(so_no_banco),
        'so_na_externa': sorted(so_na_externa),
        'em_comum': sorted(em_comum),
        'total_banco': len(banco_set),
        'total_externa': len(externa_set),
        'total_comum': len(em_comum)
    } 