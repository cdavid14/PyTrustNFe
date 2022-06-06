# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import suds
from pytrustnfe.xml import render_xml, sanitize_response
from pytrustnfe.client import get_authenticated_client
from pytrustnfe.certificado import extract_cert_and_key_from_pfx, save_cert_key
from pytrustnfe.nfe.assinatura import Assinatura
from lxml import etree


def _send(certificado, method, **kwargs):
    path = os.path.join(os.path.dirname(__file__), "templates")

    if kwargs["ambiente"] == "homologacao":
        url = "http://e-gov.betha.com.br/e-nota-contribuinte-test-ws/nfseWS?wsdl"
    else:
        url = "http://e-gov.betha.com.br/e-nota-contribuinte-ws/nfseWS?wsdl"

    xml_string_send = render_xml(path, "%s.xml" % method, False, **kwargs)

    cert, key = extract_cert_and_key_from_pfx(certificado.pfx, certificado.password)
    cert, key = save_cert_key(cert, key)
    client = get_authenticated_client(url, cert, key)

    parser = etree.XMLParser(
        remove_blank_text=True, remove_comments=True, strip_cdata=False
    )
    signer = Assinatura(certificado.pfx, certificado.password)
    xml_send = etree.fromstring(
        xml_string_send, parser=parser)
    
    if method in ['RecepcionarLoteRps','RecepcionarLoteRpsSincrono']:
        for item in kwargs["nfse"]["lista_rps"]:
            signer.assina_xml(xml_send, "rps:"+str(item["numero"])+str(item["serie"])) 
        xml_signed_send = signer.assina_xml(xml_send, "lote:"+str(kwargs["nfse"]["numero_lote"])).rstrip("\n")
    elif method == 'CancelarNfse':
        xml_signed_send = signer.assina_xml(xml_send, "1").rstrip("\n")
    elif method == 'GerarNfse':
        xml_signed_send = signer.assina_xml(xml_send, "rps:"+str(kwargs["nfse"]["numero"])+str(kwargs["nfse"]["serie"])) 
    try:
        response = getattr(client.service, method)(1, xml_signed_send)
    except suds.WebFault as e:
        return {
            "sent_xml": xml_signed_send,
            "received_xml": e.fault.faultstring,
            "object": None,
        }

    response, obj = sanitize_response(response)
    return {"sent_xml": xml_signed_send, "received_xml": response, "object": obj}


def gerar_nfse(certificado, **kwargs):
    return _send(certificado, "GerarNfse", **kwargs)


def envio_lote_rps_assincrono(certificado, **kwargs):
    return _send(certificado, "RecepcionarLoteRps", **kwargs)


def envio_lote_rps(certificado, **kwargs):
    return _send(certificado, "RecepcionarLoteRpsSincrono", **kwargs)


def cancelar_nfse(certificado, **kwargs):
    return _send(certificado, "CancelarNfse", **kwargs)


def substituir_nfse(certificado, **kwargs):
    return _send(certificado, "SubstituirNfse", **kwargs)


def consulta_situacao_lote_rps(certificado, **kwargs):
    return _send(certificado, "ConsultaSituacaoLoteRPS", **kwargs)


def consulta_nfse_por_rps(certificado, **kwargs):
    return _send(certificado, "ConsultaNfsePorRps", **kwargs)


def consultar_lote_rps(certificado, **kwargs):
    return _send(certificado, "ConsultarLoteRps", **kwargs)


def consulta_nfse_servico_prestado(certificado, **kwargs):
    return _send(certificado, "ConsultarNfseServicoPrestado", **kwargs)


def consultar_nfse_servico_tomado(certificado, **kwargs):
    return _send(certificado, "ConsultarNfseServicoTomado", **kwargs)


def consulta_nfse_faixe(certificado, **kwargs):
    return _send(certificado, "ConsultarNfseFaixa", **kwargs)


def consulta_cnpj(certificado, **kwargs):
    return _send(certificado, "ConsultaCNPJ", **kwargs)
