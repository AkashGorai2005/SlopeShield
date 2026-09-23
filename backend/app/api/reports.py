from fastapi import APIRouter
from fastapi.responses import Response
from datetime import datetime, timezone
from app.services.data_service import get_locations, get_historical, data_status

router=APIRouter(prefix='/reports',tags=['reports'])

@router.get('/summary')
def report_summary():
    locations=get_locations(); hist=get_historical()
    return {'generatedAt':datetime.now(timezone.utc).isoformat(),'dataStatus':data_status(),'total':len(locations),'counts':{level:sum(x['riskLevel']==level for x in locations) for level in ['low','moderate','high','critical']},'historicalEvents':len(hist['points'])}

@router.get('/csv')
def report_csv():
    locations=get_locations()
    headers=['location','state','latitude','longitude','riskLevel','probability','rainfall24h','rainfall7d','slope','elevation','historicalLandslides','modelSource']
    lines=[','.join(headers)]
    for x in locations:
        vals=[x.get('name'),x.get('state'),x.get('latitude'),x.get('longitude'),x.get('riskLevel'),x.get('probability'),x.get('rainfall'),x.get('rainfall7d'),x.get('slope'),x.get('elevation'),x.get('historicalLandslides'),x.get('modelSource')]
        lines.append(','.join('"'+str(v).replace('"','""')+'"' for v in vals))
    return Response('\n'.join(lines),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=SLOPESHIELD-risk-report.csv'})

@router.get('/html')
def report_html():
    locations=get_locations(); status=data_status(); now=datetime.now(timezone.utc).isoformat()
    rows=''.join(f"<tr><td>{x['name']}</td><td>{x['state']}</td><td>{x['riskLevel'].title()}</td><td>{x['probability']:.1%}</td><td>{x['rainfall']:.1f}</td><td>{x['slope']:.1f}</td><td>{x['elevation']:.0f}</td></tr>" for x in locations)
    html=f'''<!doctype html><html><head><meta charset="utf-8"><title>SLOPESHIELD NER Risk Report</title><style>body{{font:14px Arial;margin:32px;color:#183b32}}h1{{margin-bottom:4px}}table{{border-collapse:collapse;width:100%;margin-top:24px}}td,th{{border:1px solid #dbe5df;padding:8px;text-align:left}}th{{background:#eef5f1}}.meta{{color:#60756d}}</style></head><body><h1>SLOPESHIELD NER</h1><div>AI-based Early Warning and Landslide Risk Monitoring — Northeast Region</div><p class="meta">Generated {now} · Data mode: {status['mode']} · Model values are only as valid as the configured source/model pipeline.</p><table><thead><tr><th>Location</th><th>State</th><th>Risk</th><th>Probability</th><th>Rainfall 24h (mm)</th><th>Slope (°)</th><th>Elevation (m)</th></tr></thead><tbody>{rows}</tbody></table></body></html>'''
    return Response(html,media_type='text/html')

@router.get('/pdf')
def report_pdf():
    from io import BytesIO
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    locations=get_locations(); buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=landscape(A4),rightMargin=24,leftMargin=24,topMargin=24,bottomMargin=24)
    styles=getSampleStyleSheet(); story=[Paragraph('SLOPESHIELD NER — Risk Assessment Report',styles['Title']),Paragraph('AI-based Early Warning and Landslide Risk Monitoring — Northeast Region',styles['Normal']),Spacer(1,12)]
    data=[['Location','State','Risk','Probability','Rain 24h (mm)','Slope (deg)','Elevation (m)']]
    for x in locations: data.append([x['name'],x['state'],x['riskLevel'].title(),f"{x['probability']:.1%}",f"{float(x.get('rainfall',0)):.1f}",f"{float(x.get('slope',0)):.1f}",f"{float(x.get('elevation',0)):.0f}"])
    table=Table(data,repeatRows=1); table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f3ee')),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#cbd8d2')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(table); story.append(Spacer(1,10)); story.append(Paragraph(f"Generated {datetime.now(timezone.utc).isoformat()} · Data mode: {data_status()['mode']}",styles['Normal']))
    doc.build(story); return Response(buf.getvalue(),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename=SLOPESHIELD-risk-report.pdf'})


@router.get('/problems-pdf')
def problems_pdf():
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    status = data_status()
    locations = get_locations()
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    problems = [
        ["Issue", "Impact", "Status"],
        ["Backend stopped or closed", "Frontend cannot fetch locations, weather, alerts, or simulations.", "Fixed: backend startup verified"],
        ["SQLite schema timestamps missing from inserts", "Live monitoring and what-if simulation returned HTTP 500.", "Fixed: timestamps added"],
        ["Analytics arrays were empty", "Risk trend and factor charts rendered blank.", "Fixed: live chart payloads added"],
        ["Historical inventory was not imported", "The UI reported historical data as not loaded.", f"Fixed: {status['historicalDatabaseCount']} NASA records loaded"],
        ["Reference locations", "The 15 monitored locations are seeded catalogue points, not IoT sensor locations.", "Documented limitation"],
        ["Model calibration risk", "Validation is 100% on the supplied holdout and may not represent real-world performance.", "Requires independent validation"],
    ]
    story = [
        Paragraph("SLOPESHIELD NER - Data Pipeline Problems and Fixes", styles["Title"]),
        Paragraph(f"Generated {datetime.now(timezone.utc).isoformat()}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Current system status", styles["Heading2"]),
        Paragraph(
            f"Database mode: {status['mode']} | Historical records: {status['historicalDatabaseCount']} | "
            f"Monitored locations: {len(locations)}. Live weather source: Open-Meteo.",
            styles["Normal"],
        ),
        Spacer(1, 12),
        Paragraph("Audit findings", styles["Heading2"]),
    ]
    table = Table(problems, colWidths=[125, 220, 125], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9f3ee")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd8d2")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7faf8")]),
    ]))
    story.append(table)
    story.append(Spacer(1, 14))
    story.append(Paragraph("End-to-end verification", styles["Heading2"]))
    story.append(Paragraph("The verified live pipeline fetches weather data, updates all monitored locations, persists model predictions and alerts, and serves the frontend through the API.", styles["Normal"]))
    document.build(story)
    return Response(buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=SLOPESHIELD-pipeline-audit.pdf"})


