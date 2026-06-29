from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable
from pathlib import Path

OUTPUT = Path(__file__).parent / "data" / "hr_policy.pdf"

BLUE       = colors.HexColor("#1B3A6B")
LIGHT_BLUE = colors.HexColor("#EAF0FB")
MID_BLUE   = colors.HexColor("#2E5DA8")
GREY_LINE  = colors.HexColor("#B0BEC5")
ROW_ALT    = colors.HexColor("#F0F4FA")


def make_styles():
    base = getSampleStyleSheet()

    styles = {}
    styles["cover_company"] = ParagraphStyle(
        "cover_company", parent=base["Normal"],
        fontSize=26, textColor=colors.white, alignment=TA_CENTER,
        fontName="Helvetica-Bold", spaceAfter=10,
    )
    styles["cover_title"] = ParagraphStyle(
        "cover_title", parent=base["Normal"],
        fontSize=18, textColor=colors.HexColor("#D0E4FF"), alignment=TA_CENTER,
        fontName="Helvetica", spaceAfter=6,
    )
    styles["cover_meta"] = ParagraphStyle(
        "cover_meta", parent=base["Normal"],
        fontSize=11, textColor=colors.HexColor("#A0C0E8"), alignment=TA_CENTER,
        spaceAfter=4,
    )
    styles["toc_title"] = ParagraphStyle(
        "toc_title", parent=base["Normal"],
        fontSize=16, textColor=BLUE, fontName="Helvetica-Bold",
        alignment=TA_CENTER, spaceAfter=18,
    )
    styles["toc_entry"] = ParagraphStyle(
        "toc_entry", parent=base["Normal"],
        fontSize=10, textColor=colors.HexColor("#2C2C2C"),
        leftIndent=10, spaceAfter=5,
    )
    styles["intro_heading"] = ParagraphStyle(
        "intro_heading", parent=base["Normal"],
        fontSize=16, textColor=BLUE, fontName="Helvetica-Bold",
        alignment=TA_CENTER, spaceAfter=14,
    )
    styles["section"] = ParagraphStyle(
        "section", parent=base["Normal"],
        fontSize=13, textColor=BLUE, fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=8,
    )
    styles["subsection"] = ParagraphStyle(
        "subsection", parent=base["Normal"],
        fontSize=11, textColor=MID_BLUE, fontName="Helvetica-Bold",
        spaceBefore=10, spaceAfter=5,
    )
    styles["body"] = ParagraphStyle(
        "body", parent=base["Normal"],
        fontSize=10, leading=15, textColor=colors.HexColor("#2C2C2C"),
        alignment=TA_JUSTIFY, spaceAfter=6,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", parent=base["Normal"],
        fontSize=10, leading=14, leftIndent=18, bulletIndent=6,
        textColor=colors.HexColor("#2C2C2C"), spaceAfter=3,
    )
    styles["note"] = ParagraphStyle(
        "note", parent=base["Normal"],
        fontSize=9, leading=13, leftIndent=10, rightIndent=10,
        textColor=colors.HexColor("#444444"), alignment=TA_JUSTIFY,
        backColor=LIGHT_BLUE, borderPad=6, spaceAfter=8,
    )
    styles["ack"] = ParagraphStyle(
        "ack", parent=base["Normal"],
        fontSize=10, leading=14, alignment=TA_CENTER,
        textColor=colors.HexColor("#2C2C2C"), spaceAfter=6,
    )
    return styles


def divider(story):
    story.append(HRFlowable(width="100%", thickness=0.6, color=BLUE, spaceAfter=8))


def section_header(story, text, styles):
    story.append(Paragraph(text, styles["section"]))
    divider(story)


def subsection_header(story, text, styles):
    story.append(Paragraph(text, styles["subsection"]))


def body(story, text, styles):
    story.append(Paragraph(text, styles["body"]))


def bullets(story, items, styles):
    for item in items:
        story.append(Paragraph(f"• {item}", styles["bullet"]))


def note(story, text, styles):
    story.append(Paragraph(f"<i>Note: {text}</i>", styles["note"]))
    story.append(Spacer(1, 0.2*cm))


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = make_styles()
    story  = []

    # ─── COVER PAGE ───────────────────────────────────────────────────────────
    cover_bg = Table(
        [[Paragraph("Atlas Copco Airpower", styles["cover_company"])],
         [Spacer(1, 0.5*cm)],
         [Paragraph("Employee HR Policy Document", styles["cover_title"])],
         [Spacer(1, 0.4*cm)],
         [HRFlowable(width="60%", thickness=1, color=colors.HexColor("#5B8FD4"))],
         [Spacer(1, 0.4*cm)],
         [Paragraph("Version 2.0  |  Effective Date: January 2025", styles["cover_meta"])],
         [Paragraph("Prepared by: Human Resources Department", styles["cover_meta"])],
         [Paragraph("Confidential — For Internal Use Only", styles["cover_meta"])],
         ],
        colWidths=["100%"],
    )
    cover_bg.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 30),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 30),
        ("ROWHEIGHT", (0, 0), (0, 0), 2*cm),
    ]))
    story.append(Spacer(1, 5*cm))
    story.append(cover_bg)
    story.append(PageBreak())

    # ─── TABLE OF CONTENTS ────────────────────────────────────────────────────
    story.append(Paragraph("Table of Contents", styles["toc_title"]))
    divider(story)
    toc_entries = [
        ("Introduction", "3"),
        ("1.  Working Hours and Attendance", "4"),
        ("2.  Leave Policy", "5"),
        ("3.  Compensation and Benefits", "6"),
        ("4.  Code of Conduct", "7"),
        ("5.  Resignation and Separation", "8"),
        ("6.  Grievance Redressal", "9"),
        ("7.  IT and Data Security", "10"),
        ("8.  Travel and Expense Policy", "11"),
        ("9.  Performance Management", "12"),
        ("10. Employee Benefits and Perks", "13"),
        ("Acknowledgment", "15"),
    ]
    toc_data = [[Paragraph(t, styles["toc_entry"]), Paragraph(p, styles["toc_entry"])]
                for t, p in toc_entries]
    toc_table = Table(toc_data, colWidths=[14*cm, 2*cm])
    toc_table.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [ROW_ALT, colors.white]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ─── INTRODUCTION ─────────────────────────────────────────────────────────
    story.append(Paragraph("Introduction", styles["intro_heading"]))
    divider(story)

    body(story, """
    Atlas Copco Airpower is committed to fostering a workplace environment that is inclusive,
    professional, and productive for every member of our team. This HR Policy Document serves
    as the definitive reference guide for all employees, outlining the rights, responsibilities,
    expectations, and entitlements that govern employment at Atlas Copco Airpower.
    """, styles)

    body(story, """
    This document supersedes all prior HR policy communications and circulars issued before
    January 2025. All employees — regardless of grade, function, or location — are bound by
    the policies described herein. Managers and team leads are additionally responsible for
    communicating and enforcing these policies within their respective teams.
    """, styles)

    body(story, """
    Atlas Copco Airpower operates within the framework of applicable local and international
    labor laws. Where any clause in this document conflicts with a statutory provision, the
    statutory provision shall prevail. The Human Resources (HR) department is the custodian
    of this document and is responsible for periodic review, update, and communication of any
    amendments.
    """, styles)

    subsection_header(story, "Scope of This Policy", styles)
    body(story, """
    These policies apply to all full-time, part-time, and fixed-term contract employees of
    Atlas Copco Airpower. Policies specific to contractual workers, interns, or third-party
    vendors shall be governed by their respective agreements and supplementary HR guidelines.
    """, styles)

    subsection_header(story, "Policy Review Cycle", styles)
    body(story, """
    This HR Policy Document is reviewed annually by the HR Leadership Team in consultation
    with Legal, Finance, and Business Heads. Interim revisions may be issued when necessitated
    by regulatory changes or significant organizational restructuring. Employees will be notified
    of any material changes via official email and updated copies will be posted on the internal
    HR portal.
    """, styles)

    subsection_header(story, "How to Use This Document", styles)
    body(story, """
    Each section of this document addresses a distinct area of HR policy. Employees are
    encouraged to read the complete document upon joining and to revisit relevant sections as
    needed. For specific queries not addressed herein, employees should contact the HR helpdesk
    at hr@atlascopcoairpower.com or raise a ticket via the HR self-service portal.
    """, styles)

    note(story, "Digital copies of this document are available on the company intranet. Hard copies can be obtained from the HR department upon request.", styles)

    story.append(PageBreak())

    # ─── SECTION 1: WORKING HOURS AND ATTENDANCE ──────────────────────────────
    section_header(story, "1. Working Hours and Attendance", styles)

    subsection_header(story, "1.1 Standard Office Hours", styles)
    body(story, """
    The standard working hours at Atlas Copco Airpower are from 9:00 AM to 5:00 PM, Monday
    through Friday. This constitutes an eight-hour working day with a one-hour unpaid lunch
    break, resulting in a total of seven productive working hours per day and thirty-five hours
    per week. Public holidays notified by the company for the calendar year are excluded from
    this schedule.
    """, styles)

    subsection_header(story, "1.2 Flexible Working Window", styles)
    body(story, """
    To support a healthy work-life balance, Atlas Copco Airpower offers a flexible working
    window for employees. Employees may choose to begin work anytime between 8:00 AM and
    10:00 AM, provided they complete their required seven hours each day.
    """, styles)
    body(story, """
    However, all employees must be available and actively working during the core hours of
    11:00 AM to 4:00 PM. These core hours are non-negotiable and are designated to facilitate
    team collaboration, meetings, and real-time communication. Absence during core hours
    without prior approval from the reporting manager will be treated as half-day leave.
    """, styles)

    subsection_header(story, "1.3 Work From Home (WFH) Policy", styles)
    body(story, """
    Atlas Copco Airpower recognizes the value of flexible working arrangements and permits
    eligible employees to work from home for up to two days per week. WFH arrangements must
    be approved in advance by the employee's direct manager. Ad-hoc or last-minute WFH
    requests must be communicated and acknowledged via email or the HR self-service portal
    before the start of the working day.
    """, styles)
    body(story, """
    Employees working from home are expected to maintain the same level of availability,
    responsiveness, and productivity as they would in the office. They must be reachable on
    all standard communication channels (email, Teams, phone) during core hours. WFH is a
    privilege and may be revoked if misused or if performance is adversely affected.
    """, styles)
    bullets(story, [
        "WFH is not applicable during the first 90 days of employment (probation period).",
        "Roles requiring physical presence (lab, manufacturing, facilities) are exempt from WFH.",
        "WFH days cannot be carried over or accumulated.",
        "On-site attendance is mandatory on days with scheduled all-hands meetings or client visits.",
    ], styles)

    subsection_header(story, "1.4 Attendance Tracking", styles)
    body(story, """
    Attendance is recorded through the company's biometric system at office entry points or
    via the official attendance mobile application for remote workers. Employees are required
    to mark their check-in and check-out each day without exception. Failure to mark attendance
    on two or more occasions in a month without valid reason may result in a salary deduction
    for those days.
    """, styles)
    body(story, """
    The HR department generates monthly attendance reports for all managers. Employees with
    attendance below 85% in any given month (excluding approved leaves) will be flagged for
    a discussion with their manager. Persistent attendance issues may be escalated to the
    HR Business Partner and may form part of the employee's performance review.
    """, styles)

    subsection_header(story, "1.5 Overtime and Compensatory Off", styles)
    body(story, """
    Work beyond standard hours is generally discouraged as a routine practice. Where overtime
    is required due to business-critical needs, it must be pre-approved by the department head.
    Compensatory off (comp-off) will be granted for approved overtime at a ratio of 1:1 and
    must be availed within 30 days of the overtime worked. Comp-off days do not carry any
    monetary value and cannot be encashed.
    """, styles)

    story.append(PageBreak())

    # ─── SECTION 2: LEAVE POLICY ──────────────────────────────────────────────
    section_header(story, "2. Leave Policy", styles)

    body(story, """
    Atlas Copco Airpower's Leave Policy is designed to ensure that employees have adequate
    rest, can manage personal emergencies, and attend to family responsibilities without
    financial stress. All leave entitlements are calculated on a calendar-year basis (January
    to December) unless stated otherwise. Leave must be applied for in advance through the
    HR self-service portal, except in cases of emergency.
    """, styles)

    subsection_header(story, "2.1 Leave Entitlement Summary", styles)

    leave_data = [
        ["Leave Type", "Entitlement", "Carry Forward", "Notes"],
        ["Casual Leave (CL)", "25 days/year", "Not allowed", "For personal or family needs"],
        ["Sick Leave (SL)", "5 days/year", "Not allowed", "Medical certificate required >2 days"],
        ["Earned Leave (EL)", "15 days/year", "Up to 30 days", "Encashable on separation"],
        ["Maternity Leave", "26 weeks", "N/A", "As per statutory provision"],
        ["Paternity Leave", "5 days", "N/A", "Within 30 days of child's birth"],
        ["Bereavement Leave", "3 days", "N/A", "Immediate family members"],
        ["Marriage Leave", "5 days", "N/A", "Once during service tenure"],
    ]
    leave_table = Table(leave_data, colWidths=[4*cm, 3*cm, 3*cm, 6*cm])
    leave_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [ROW_ALT, colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_LINE),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(leave_table)
    story.append(Spacer(1, 0.4*cm))

    subsection_header(story, "2.2 Leave Application Process", styles)
    body(story, """
    All leaves must be applied for through the HR self-service portal at least 48 hours in
    advance for planned leaves, and within 24 hours of return for unplanned emergency leaves.
    The employee's manager will approve or reject the request within one business day. Leaves
    taken without approval will be treated as Loss of Pay (LOP) unless subsequently regularized
    by the manager.
    """, styles)

    subsection_header(story, "2.3 Leave Without Pay (LWP)", styles)
    body(story, """
    Employees who have exhausted their leave balance may apply for Leave Without Pay with
    documented justification. LWP requires dual approval from the reporting manager and the
    HR Business Partner. LWP days are deducted from the monthly salary proportionally and
    are reflected in the payroll for the respective month.
    """, styles)

    subsection_header(story, "2.4 Maternity and Paternity Leave", styles)
    body(story, """
    Atlas Copco Airpower fully supports working parents. Maternity Leave of 26 weeks is
    provided in accordance with statutory requirements. Employees returning from maternity
    leave are entitled to a reintegration meeting with their manager and HR to plan a
    smooth transition back to work. Paternity Leave of 5 days must be availed within 30
    days of the child's birth or adoption.
    """, styles)

    story.append(PageBreak())

    # ─── SECTION 3: COMPENSATION AND BENEFITS ────────────────────────────────
    section_header(story, "3. Compensation and Benefits", styles)

    subsection_header(story, "3.1 Salary Payment", styles)
    body(story, """
    All employees of Atlas Copco Airpower receive their monthly salary on the first working
    day of each month. Salaries are disbursed via direct bank transfer to the employee's
    registered bank account. The payslip for each month is made available on the HR portal
    by the 5th of the following month. Employees are encouraged to review their payslips
    and report any discrepancies to the payroll team within 7 days of issuance.
    """, styles)

    subsection_header(story, "3.2 Salary Structure", styles)
    body(story, """
    The salary structure at Atlas Copco Airpower is designed to be competitive and
    transparent. A typical CTC (Cost to Company) package comprises Basic Salary, House
    Rent Allowance (HRA), Special Allowance, Provident Fund (employer contribution), and
    other variable components. A detailed salary break-up is shared with employees at the
    time of joining and during annual appraisals.
    """, styles)

    subsection_header(story, "3.3 Performance Bonus", styles)
    body(story, """
    Eligible employees may receive an annual performance bonus of up to 10% of their annual
    CTC. The bonus is directly linked to the individual's annual performance rating and the
    company's overall financial performance for the year. Bonus payouts are processed in
    February following the completion of the annual performance review cycle in January.
    """, styles)
    bullets(story, [
        "Outstanding: Up to 10% of annual CTC",
        "Exceeds Expectations: Up to 7.5% of annual CTC",
        "Meets Expectations: Up to 5% of annual CTC",
        "Needs Improvement / Unsatisfactory: Not eligible for bonus",
    ], styles)
    body(story, """
    Employees who join mid-year are eligible for a pro-rated bonus based on the number of
    months of service completed before December 31st of that year. A minimum of six months
    of service is required for bonus eligibility in a given year.
    """, styles)

    subsection_header(story, "3.4 Health Insurance", styles)
    body(story, """
    Atlas Copco Airpower provides comprehensive health insurance coverage equivalent to 1%
    of the employee's annual CTC. The insurance coverage extends to the employee's immediate
    family, including spouse and up to two dependent children. The insurance plan covers
    hospitalization, pre- and post-hospitalization expenses, and day-care procedures, subject
    to policy terms. Details of the insurance plan, including the list of network hospitals
    and claim procedures, are provided in the Health Insurance Guide available on the HR portal.
    """, styles)

    subsection_header(story, "3.5 Meal Allowance", styles)
    body(story, """
    All employees are entitled to a meal allowance of 500 EUR per month. This allowance is
    credited to the employee's meal card or added directly to the salary, depending on the
    country of employment. The meal allowance is exempt from income tax up to the statutory
    limit and is non-encashable at separation.
    """, styles)

    story.append(PageBreak())

    # ─── SECTION 4: CODE OF CONDUCT ───────────────────────────────────────────
    section_header(story, "4. Code of Conduct", styles)

    body(story, """
    Atlas Copco Airpower expects all employees to conduct themselves with the highest
    standards of professionalism, integrity, and respect at all times. The Code of Conduct
    is not merely a set of rules but a reflection of the company's core values: Innovation,
    Accountability, Collaboration, and Excellence. Violations of the Code of Conduct are
    treated seriously and may result in disciplinary action up to and including termination.
    """, styles)

    subsection_header(story, "4.1 Dress Code", styles)
    body(story, """
    The standard dress code at Atlas Copco Airpower is business casual. Employees are
    expected to dress neatly and professionally at all times. On days when clients,
    auditors, or senior leadership are visiting, employees are required to wear formal
    business attire. Employees on client site visits must always wear formal attire unless
    the client's dress code is explicitly more casual, in which case manager approval is
    required.
    """, styles)

    subsection_header(story, "4.2 Professional Behaviour", styles)
    body(story, """
    Every employee is expected to treat colleagues, clients, vendors, and stakeholders with
    dignity and respect. Discrimination, harassment, bullying, or intimidation of any form
    — whether based on gender, race, religion, nationality, age, disability, or sexual
    orientation — is strictly prohibited and will be acted upon with zero tolerance.
    Employees who witness or experience such behaviour are encouraged to report it
    immediately through the Grievance Redressal process outlined in Section 6.
    """, styles)

    subsection_header(story, "4.3 Company Property", styles)
    body(story, """
    All equipment, software, and assets provided to the employee by Atlas Copco Airpower
    — including but not limited to laptops, mobile phones, access cards, and uniforms —
    remain the property of the company at all times. Upon resignation, retirement, or
    termination, employees must return all company assets in good working condition within
    their last working day. Outstanding asset returns will result in a hold on the final
    settlement.
    """, styles)

    subsection_header(story, "4.4 Confidentiality Obligations", styles)
    body(story, """
    Employees are required to sign a Confidentiality and Non-Disclosure Agreement (NDA) at
    the time of joining. This agreement extends for a period of 2 years post-employment,
    during which former employees must not disclose, use, or transfer any proprietary
    information, trade secrets, customer data, or internal business strategies belonging
    to Atlas Copco Airpower. Breach of this clause may result in legal action.
    """, styles)

    subsection_header(story, "4.5 Conflict of Interest", styles)
    body(story, """
    Employees must avoid situations where personal interests could conflict with those of
    the company. This includes undisclosed employment with competitors, accepting gifts
    or favours from vendors beyond a nominal value of 50 EUR, or having a financial
    interest in a competing business. Any potential conflict of interest must be declared
    to HR and the employee's manager at the earliest opportunity.
    """, styles)

    story.append(PageBreak())

    # ─── SECTION 5: RESIGNATION AND SEPARATION ────────────────────────────────
    section_header(story, "5. Resignation and Separation", styles)

    body(story, """
    The separation of an employee from Atlas Copco Airpower — whether voluntary or
    involuntary — is handled with professionalism, fairness, and confidentiality. The
    processes outlined in this section are designed to ensure a smooth transition for
    both the employee and the organization.
    """, styles)

    subsection_header(story, "5.1 Voluntary Resignation", styles)
    body(story, """
    Employees who wish to resign must submit a formal written resignation letter to their
    reporting manager and HR Business Partner. The resignation letter must clearly state
    the intended last working day, which must comply with the notice period requirements.
    Verbal resignations are not accepted and do not trigger the notice period.
    """, styles)

    subsection_header(story, "5.2 Notice Period", styles)
    body(story, """
    The standard notice period for all employees at Atlas Copco Airpower is 60 calendar
    days. This applies to both voluntary resignation by the employee and termination
    initiated by the company. The notice period may be waived or reduced with written
    approval from the employee's manager in consultation with the HR Business Partner.
    """, styles)
    body(story, """
    During the notice period, the employee is expected to continue performing their
    regular duties, complete knowledge transfer documentation, and assist in the handover
    of responsibilities to a designated colleague or replacement. Non-compliance during
    the notice period may affect the final settlement and reference letters.
    """, styles)

    subsection_header(story, "5.3 Notice Period Buyout", styles)
    body(story, """
    Employees who are unable to serve the full notice period may opt for a notice period
    buyout. The buyout amount is calculated at the employee's basic salary rate for the
    remaining days of the notice period. The buyout amount must be paid to the company
    before or on the last working day. The company may also initiate a notice period
    buyout for business reasons, in which case the payment will be made to the employee.
    """, styles)

    subsection_header(story, "5.4 Exit Interview", styles)
    body(story, """
    All departing employees are invited to participate in an exit interview conducted by
    the HR Business Partner. The exit interview is an opportunity for the employee to
    share candid feedback about their experience at Atlas Copco Airpower. Responses are
    treated confidentially and used to improve the work environment. Participation is
    voluntary but highly encouraged.
    """, styles)

    subsection_header(story, "5.5 Full and Final Settlement", styles)
    body(story, """
    The full and final (F&F) settlement, including pending salary, earned leave
    encashment, and any reimbursable expenses, will be processed and credited to the
    employee's bank account within 45 calendar days of the last working day. The F&F
    settlement is contingent upon the employee returning all company assets, completing
    the clearance process, and submitting all pending expense claims.
    """, styles)

    story.append(PageBreak())

    # ─── SECTION 6: GRIEVANCE REDRESSAL ───────────────────────────────────────
    section_header(story, "6. Grievance Redressal", styles)

    body(story, """
    Atlas Copco Airpower is committed to providing a fair, timely, and transparent
    mechanism for employees to raise and resolve workplace grievances. All complaints are
    treated with confidentiality and are investigated impartially. Employees are encouraged
    to use this mechanism without fear of retaliation.
    """, styles)

    subsection_header(story, "6.1 Scope of Grievances", styles)
    body(story, """
    A grievance is any concern, dissatisfaction, or complaint that an employee believes
    is unjust, unfair, or inconsistent with company policy. Grievances may relate to
    compensation, working conditions, interpersonal conflict, harassment, discrimination,
    or concerns about manager conduct. Concerns related to ethics violations should be
    reported through the Ethics Hotline rather than the Grievance process.
    """, styles)

    subsection_header(story, "6.2 Three-Step Escalation Process", styles)
    body(story, "The following escalation process must be followed:", styles)

    cell_style = ParagraphStyle(
        "steps_cell", fontSize=9, leading=12,
        textColor=colors.HexColor("#2C2C2C"), alignment=TA_LEFT,
    )
    head_style = ParagraphStyle(
        "steps_head", fontSize=9, leading=12,
        textColor=colors.white, fontName="Helvetica-Bold", alignment=TA_LEFT,
    )
    steps_data = [
        [Paragraph("Step", head_style), Paragraph("Action", head_style), Paragraph("Timeline", head_style)],
        [Paragraph("Step 1", cell_style),
         Paragraph("Raise the concern directly with the reporting manager. A resolution should be sought informally through open dialogue.", cell_style),
         Paragraph("Within 5 working days", cell_style)],
        [Paragraph("Step 2", cell_style),
         Paragraph("If unresolved, escalate the grievance formally to the HR Business Partner by submitting a written grievance form. HR will investigate and respond.", cell_style),
         Paragraph("Within 7 days of Step 1", cell_style)],
        [Paragraph("Step 3", cell_style),
         Paragraph("If still unresolved, escalate to senior leadership (Business Head / CHRO). A formal review committee will be convened.", cell_style),
         Paragraph("Within 15 days of Step 2", cell_style)],
    ]
    steps_table = Table(steps_data, colWidths=[2*cm, 10*cm, 4*cm])
    steps_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), BLUE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [ROW_ALT, colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_LINE),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    story.append(steps_table)
    story.append(Spacer(1, 0.4*cm))

    subsection_header(story, "6.3 Anti-Retaliation Policy", styles)
    body(story, """
    Atlas Copco Airpower strictly prohibits any form of retaliation against an employee
    who raises a grievance in good faith. Retaliation includes, but is not limited to,
    unfair performance ratings, exclusion from opportunities, reassignment of duties,
    or any form of intimidation. Any act of retaliation will itself be treated as a
    serious disciplinary offence.
    """, styles)

    story.append(PageBreak())

    # ─── SECTION 7: IT AND DATA SECURITY ──────────────────────────────────────
    section_header(story, "7. IT and Data Security", styles)

    body(story, """
    The secure management of information and technology assets is a shared responsibility
    of all employees at Atlas Copco Airpower. These policies are designed to protect
    company data, client information, and the integrity of IT systems from unauthorized
    access, misuse, or breach.
    """, styles)

    subsection_header(story, "7.1 Password Management", styles)
    body(story, """
    All employees must adhere to the company's password policy at all times. Passwords
    must be a minimum of 12 characters in length and must include a combination of
    uppercase letters, lowercase letters, numbers, and special characters. Passwords must
    be changed every 90 days. Employees must not reuse any of their last 10 passwords.
    Sharing passwords with colleagues — even managers — is strictly prohibited.
    """, styles)

    subsection_header(story, "7.2 Personal Device Policy (BYOD)", styles)
    body(story, """
    Personal devices, including smartphones, tablets, and laptops, are not permitted on
    the company's internal network without explicit prior approval from the IT Security
    team. Employees seeking to connect personal devices must submit a formal BYOD request
    and comply with the Mobile Device Management (MDM) requirements as prescribed by IT.
    """, styles)

    subsection_header(story, "7.3 Data Classification", styles)
    body(story, """
    All data handled by employees must be classified according to the following framework
    and treated accordingly:
    """, styles)
    bullets(story, [
        "Public: Data approved for external distribution. No restrictions.",
        "Internal: Data for internal use only. Not to be shared with external parties.",
        "Confidential: Sensitive business or client data. Encryption required in transit and at rest.",
        "Restricted: Highly sensitive data (financial records, PII, IP). Access limited to authorized personnel only.",
    ], styles)

    subsection_header(story, "7.4 Acceptable Use of IT Resources", styles)
    body(story, """
    Company IT resources — including computers, email, internet access, and software
    licenses — are provided for business purposes. Incidental personal use is permitted
    provided it does not interfere with work, violate any law, or compromise security.
    The company reserves the right to monitor usage of IT resources in accordance with
    applicable law and the employee's consent provided at the time of joining.
    """, styles)

    subsection_header(story, "7.5 Security Incident Reporting", styles)
    body(story, """
    Any actual or suspected security incident — including phishing attempts, data breaches,
    lost or stolen devices, unauthorized access, or malware infections — must be reported
    to the IT Security team within 2 hours of discovery. Delayed reporting of a security
    incident is itself a policy violation and may result in disciplinary action. The IT
    Security team's emergency contact is available 24/7 on the intranet.
    """, styles)

    story.append(PageBreak())

    # ─── SECTION 8: TRAVEL AND EXPENSE POLICY ────────────────────────────────
    section_header(story, "8. Travel and Expense Policy", styles)

    body(story, """
    Atlas Copco Airpower reimburses employees for reasonable and necessary business travel
    expenses incurred while carrying out their professional responsibilities. All travel
    must be planned, approved, and documented in accordance with this policy to qualify
    for reimbursement.
    """, styles)

    subsection_header(story, "8.1 Domestic Travel Limits", styles)
    travel_data = [
        ["City Category", "Hotel (per night)", "Meals (per day)", "Local Transport"],
        ["Metro Cities", "Up to 200 EUR", "Up to 100 EUR", "Actuals with receipts"],
        ["Tier 2 Cities", "Up to 100 EUR", "Up to 100 EUR", "Actuals with receipts"],
    ]
    travel_table = Table(travel_data, colWidths=[4.5*cm, 3.5*cm, 3.5*cm, 4.5*cm])
    travel_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [ROW_ALT, colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_LINE),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(travel_table)
    story.append(Spacer(1, 0.3*cm))

    body(story, """
    Employees are expected to book hotels and flights in advance through the company's
    approved travel portal to take advantage of negotiated corporate rates. Bookings made
    outside the approved portal will be reimbursed only up to the policy limit and require
    additional justification.
    """, styles)

    subsection_header(story, "8.2 International Travel", styles)
    body(story, """
    International travel must be pre-approved by the Vice President (VP) of the
    respective function at least 10 business days before the travel date. Travel requests
    must be submitted via the HR portal along with a business justification, estimated
    budget, and agenda. Visa and travel insurance arrangements are facilitated by the
    travel desk upon confirmation of VP approval.
    """, styles)

    subsection_header(story, "8.3 Expense Claims and Reimbursement", styles)
    body(story, """
    All expenses must be submitted within 30 days of the travel date with original
    receipts or e-receipts. Claims submitted after 30 days will require Finance Head
    approval and may be declined if the delay is unexplained. Approved reimbursements
    are processed and credited to the employee's salary account within 15 working days
    of submission.
    """, styles)

    story.append(PageBreak())

    # ─── SECTION 9: PERFORMANCE MANAGEMENT ───────────────────────────────────
    section_header(story, "9. Performance Management", styles)

    body(story, """
    Atlas Copco Airpower's Performance Management System (PMS) is designed to align
    individual goals with the organization's strategic objectives, recognize high
    performance, identify development needs, and support career growth. The system is
    built on the principles of transparency, continuous feedback, and objective
    assessment.
    """, styles)

    subsection_header(story, "9.1 Goal Setting", styles)
    body(story, """
    At the beginning of each year (January), employees and managers collaborate to set
    SMART (Specific, Measurable, Achievable, Relevant, Time-bound) goals. Goals are
    entered into the HR performance system and are visible to both the employee and the
    manager. Goals may be revised mid-year with mutual agreement if business priorities
    change significantly.
    """, styles)

    subsection_header(story, "9.2 Continuous Feedback and Mid-Year Check-in", styles)
    body(story, """
    Managers are expected to provide regular, ongoing feedback to their team members
    throughout the year. A formal mid-year check-in is conducted in July to review
    progress against goals, address development needs, and recalibrate priorities if
    required. Employees may also request feedback from their managers at any time
    through the HR portal's feedback module.
    """, styles)

    subsection_header(story, "9.3 Annual Performance Review", styles)
    body(story, """
    The annual performance review takes place in January each year and covers the
    preceding calendar year (January to December). The review involves a self-assessment
    by the employee, an assessment by the reporting manager, and a calibration discussion
    at the department level to ensure consistency and fairness. Final ratings are
    communicated to employees by the end of February.
    """, styles)

    subsection_header(story, "9.4 Performance Ratings", styles)
    rating_data = [
        ["Rating",               "Description"],
        ["Outstanding (O)",          "Consistently exceeds all goals; significant impact on business outcomes"],
        ["Exceeds Expectations (EE)", "Exceeds most goals; demonstrates initiative and strong results"],
        ["Meets Expectations (ME)",   "Achieves all set goals; solid and reliable performer"],
        ["Needs Improvement (NI)",    "Partially meets goals; requires targeted improvement plan"],
        ["Unsatisfactory (U)",        "Fails to meet goals; performance is below acceptable threshold"],
    ]
    rating_table = Table(rating_data, colWidths=[5.5*cm, 10.5*cm])
    rating_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [ROW_ALT, colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_LINE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(rating_table)
    story.append(Spacer(1, 0.3*cm))

    subsection_header(story, "9.5 Performance Improvement Plan (PIP)", styles)
    body(story, """
    Employees rated Needs Improvement or Unsatisfactory may be placed on a Performance
    Improvement Plan (PIP). The PIP is a structured 60-day program with clearly defined
    improvement targets, weekly check-in meetings with the manager and HR Business
    Partner, and documented milestones. The purpose of the PIP is to support the
    employee in achieving the required performance standard. Failure to meet PIP
    objectives may result in further disciplinary action, including separation.
    """, styles)

    story.append(PageBreak())

    # ─── SECTION 10: EMPLOYEE BENEFITS AND PERKS ─────────────────────────────
    section_header(story, "10. Employee Benefits and Perks", styles)

    body(story, """
    Atlas Copco Airpower believes that a motivated and well-supported workforce is the
    foundation of business success. Beyond competitive compensation, the company offers
    a comprehensive benefits package aimed at supporting employee wellbeing, long-term
    financial security, and professional development.
    """, styles)

    subsection_header(story, "10.1 Provident Fund (PF)", styles)
    body(story, """
    The company contributes 12% of the employee's basic salary towards the Provident
    Fund upon completion of 2 years of continuous service. The employee's own PF
    contribution is deducted from gross salary as per the statutory rate. PF accounts
    are managed in accordance with applicable regulations, and employees can access
    their PF balance through the government's unified portal or the company's HR
    self-service system.
    """, styles)
    body(story, """
    Employees may apply for a PF advance in cases of emergency such as illness,
    marriage, or purchase of a home, subject to fund availability and eligibility
    criteria prescribed by the regulatory authority.
    """, styles)

    subsection_header(story, "10.2 Gratuity", styles)
    body(story, """
    Employees who have completed a minimum of 5 years of continuous service at Atlas
    Copco Airpower are entitled to receive gratuity at the time of separation. Gratuity
    is calculated as per the statutory formula: (Last drawn basic salary × 15 days ×
    Number of years of service) / 26. Gratuity is paid within 30 days of the employee's
    last working day.
    """, styles)

    subsection_header(story, "10.3 Learning and Development (L&D) Sponsorship", styles)
    body(story, """
    Atlas Copco Airpower is committed to the continuous professional development of its
    workforce. Every employee is entitled to 2 company-sponsored certifications per
    calendar year, with a cap of 500 EUR per certification. Eligible certifications
    include industry-recognized credentials in areas such as technology, engineering,
    project management, finance, and leadership.
    """, styles)
    body(story, """
    To avail the L&D sponsorship, employees must submit a training request through the
    HR portal with a description of the certification, its business relevance, and the
    estimated cost. Requests must be approved by the reporting manager and the L&D team
    before enrollment. Employees who leave within 12 months of completing a company-
    sponsored certification may be required to repay the full or partial training cost,
    as stipulated in the Training Bond Agreement.
    """, styles)

    subsection_header(story, "10.4 Annual Team Offsite", styles)
    body(story, """
    Each team at Atlas Copco Airpower is entitled to one annual offsite — fully funded
    by the company — to promote team bonding, strategic alignment, and collective
    rejuvenation. The offsite is typically organized between Q2 and Q3, and the location,
    agenda, and budget are planned by the team in coordination with the department head.
    The company covers all costs including travel, accommodation, meals, and planned
    activities.
    """, styles)

    subsection_header(story, "10.5 Additional Perks", styles)
    bullets(story, [
        "Employee Assistance Programme (EAP): Free and confidential counselling sessions available to all employees and their immediate family members.",
        "Referral Bonus: Employees who refer successful candidates for open positions receive a referral bonus as per the Talent Acquisition policy.",
        "Wellness Programme: Subsidized gym memberships and access to virtual wellness sessions.",
        "Flexible Benefits Plan: Employees above a certain grade can customize components of their CTC within defined limits through the flexible benefits portal.",
        "Long Service Awards: Recognition and rewards for employees completing 5, 10, and 15 years of service.",
    ], styles)

    story.append(PageBreak())

    # ─── ACKNOWLEDGMENT PAGE ──────────────────────────────────────────────────
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("Employee Acknowledgment", styles["intro_heading"]))
    divider(story)

    body(story, """
    I, the undersigned, acknowledge that I have received, read, and understood the
    Atlas Copco Airpower Employee HR Policy Document (Version 2.0, effective January 2025).
    I agree to abide by all the policies, procedures, and guidelines outlined in this
    document. I understand that failure to comply with these policies may result in
    disciplinary action, up to and including termination of employment.
    """, styles)

    body(story, """
    I further acknowledge that this document does not constitute a contract of employment
    and that Atlas Copco Airpower reserves the right to amend, update, or revoke any
    policy herein at any time, with reasonable notice to employees.
    """, styles)

    story.append(Spacer(1, 2*cm))

    sig_data = [
        ["Employee Full Name:", "___________________________________"],
        ["Employee ID:",        "___________________________________"],
        ["Department:",         "___________________________________"],
        ["Date:",               "___________________________________"],
        ["Signature:",          "___________________________________"],
    ]
    sig_table = Table(sig_data, colWidths=[5*cm, 10*cm])
    sig_table.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("ALIGN",         (0, 0), (0, -1), "RIGHT"),
    ]))
    story.append(sig_table)

    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(
        "For HR use only — Please retain the signed copy in the employee's personnel file.",
        styles["ack"]
    ))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREY_LINE))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Atlas Copco Airpower | Human Resources Department | hr@atlascopcoairpower.com",
        styles["ack"]
    ))

    doc.build(story)

    size = OUTPUT.stat().st_size
    print(f"PDF created : {OUTPUT}")
    print(f"File size   : {size:,} bytes  ({size/1024:.1f} KB)")


if __name__ == "__main__":
    build_pdf()
