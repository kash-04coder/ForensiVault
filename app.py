import streamlit as st
import sqlite3
import pandas as pd

from tamper import create_alert
from verification import save_verification
from dashboard import get_dashboard_data
from metadata import (
    extract_image_metadata,
    extract_pdf_metadata
)
from case_manager import *
from evidence_details import get_evidence_details
from timeline import get_timeline
from report_generator import generate_report
from database import init_db
from auth import (
    create_default_admin,
    login,
    create_user,
    delete_user,
    update_role,
    get_users
)
from audit import (
    log_action,
    get_audit_logs,
    get_audit_users
)
from case_report import generate_case_report
from evidence import calculate_hash, save_evidence
from datetime import datetime

def load_css():
    with open("assets/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
load_css()

init_db()
create_default_admin()

st.set_page_config(
    page_title="ForensiVault",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# LOGIN PAGE
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        st.markdown("""
        <div style="
        background:#1E293B;
        padding:25px;
        border-radius:15px;
        margin-bottom:20px;
        ">

        <h1 style="color:white;">
        🔐 ForensiVault
        </h1>
                    
        <h2 style="color:white;">
        🛡 Digital Evidence Management System
        </h2>

        <p style="color:#CBD5E1;">
        Secure Digital Forensics • Chain of Custody • SHA256 Verification
        </p>

        </div>
        """, unsafe_allow_html=True)
        
        left, right = st.columns([1.2,1])
        with left:
            st.image("assets/forensic1.jpg", width=500)
            # st.markdown(
            #     """
            #     <div style="display: flex; justify-content: center;">
            #         <img src="assets/forensic.jpg" width="300">
            #     </div>
            #     """,
            #     unsafe_allow_html=True
            # )
            
        with right:
            st.subheader("Login")
            username = st.text_input(
                "Username",
                key="login_user"
            )
            password = st.text_input(
                "Password",
                type="password",
                key="login_pass"
            )
            if st.button("Login"):
                role = login(
                    username,
                    password
                )
                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error(
                        "Invalid Credentials"
                    )
    
            st.write("Don't have an account?")
            if st.button("Register Here"):
                st.session_state.page = "register"
                st.rerun()
        
        st.markdown("""
        ### Why DEMS?
        ✔ Secure Evidence Storage
        ✔ SHA-256 Integrity Verification
        ✔ Chain of Custody
        ✔ Metadata Analysis
        ✔ Tamper Detection
        ✔ Digital Investigation Reports
        """)

    else:
        st.subheader("Register")
        new_username = st.text_input(
            "Choose Username",
            key="register_user"
        )
        new_password = st.text_input(
            "Choose Password",
            type="password",
            key="register_pass"
        )
        confirm = st.text_input(
            "Re-type Password",
            type="password",
            key="confirm_pass"
        )
        if st.button("Register"):
            if new_password != confirm:
                st.error("Passwords do not match.")
            success = create_user(
                new_username,
                new_password,
                "Viewer"
            )
            if success:
                st.success(
                    "Account Created Successfully"
                )
            else:
                st.error(
                    "Username Already Exists"
                )
    
        st.write("Already have an account?")
        if st.button("Login Here"):
            st.session_state.page = "login"
            st.rerun()


# DASHBOARD
else:

    menu_items = [
            "Dashboard",
            # "View Evidence",
            "Evidence Timeline",
            "Evidence Search",
            "Metadata Analysis",
            # "Tamper Alerts",
            "Evidence Details",
            "Activity Monitoring",
            # "Audit Logs"
        ]

    if st.session_state.role == "Admin":
        menu_items.extend([
            "Case Management",
            # "Register Evidence",
            "Verify Evidence",
            "Chain of Custody",
            "Generate Report",
            "Secure Evidence Vault",
            "User Management"
        ])
    elif st.session_state.role == "Investigator":
        menu_items.extend([
            "Case Management",
            # "Register Evidence",
            "Chain of Custody",
            "Generate Report"
        ])
    elif st.session_state.role == "Analyst":
        menu_items.extend([
            "Verify Evidence",
            "Generate Report",
            "Secure Evidence Vault"
        ])
    elif st.session_state.role == "Viewer":
        pass

    st.sidebar.markdown("""
        # 🛡 DEMS
        Welcome,
        **{}**
        """.format(
            st.session_state.username,
        ))
    st.sidebar.success(
        f"Role: {st.session_state.role}"
    )
    menu = st.sidebar.selectbox(
        "Menu",
        menu_items
    )

    if menu == "Dashboard":

        st.title("🛡 Digital Evidence Management System")
        st.success(
            f"Welcome {st.session_state.username}"
        )
        data, uploads, roles, activity = get_dashboard_data()
        col1,col2,col3,col4,col5 = st.columns(5)
        col1.metric(
            "📂 Evidence",
            data["evidence"]
        )
        col2.metric(
            "👥 Users",
            data["users"]
        )
        col3.metric(
            "🚨 Alerts",
            data["alerts"]
        )
        col4.metric(
            "✅ Verified",
            data["verified"]
        )
        col5.metric(
            "⚠ Tampered",
            data["tampered"]
        )

        total = data["verified"] + data["tampered"]
        if total == 0:
            health = 100

        else:
            health = round(
                data["verified"]/total*100,
                1
            )

        st.progress(health/100)
        st.success(
            f"System Integrity Score : {health}%"
        )
        
        if not uploads.empty:
            uploads["upload_time"] = pd.to_datetime(
                uploads["upload_time"]
            )
            uploads["Date"] = uploads[
                "upload_time"
            ].dt.date
            chart = uploads.groupby(
                "Date"
            ).size()
            st.subheader("📈 Evidence Upload Trend")
            st.line_chart(chart)
        

        st.subheader("👥 User Roles")
        roles = roles.set_index("role")
        st.bar_chart(roles)

        st.subheader("🕒 Recent Activity")
        st.dataframe(
            activity,
            use_container_width=True
        )





#------------------------------------------------------------------------------------------

    # elif menu == "Register Evidence":

    #     if st.session_state.role not in [
    #         "Admin",
    #         "Investigator"
    #     ]:
    #         st.error("Access Denied")
    #         st.stop()

    #     st.header("Evidence Registration")

    #     case_id = st.text_input("Case ID")
    #     title = st.text_input("Evidence Title")

    #     uploaded_file = st.file_uploader(
    #         "Upload Evidence"
    #     )

    #     if st.button("Save Evidence"):

    #         if uploaded_file:
    #             evidence_hash = save_evidence(
    #                 case_id,
    #                 title,
    #                 uploaded_file,
    #                 st.session_state.username
    #             )

    #             log_action(
    #                 st.session_state.username,
    #                 f"Uploaded {title}"
    #             )

    #             st.success("Evidence Stored")

    #             st.code(evidence_hash)

    # elif menu == "View Evidence":
    #     st.title("📂 Evidence Repository")
    #     conn = sqlite3.connect("forensic.db")
    #     evidence = conn.execute(
    #         "SELECT * FROM evidence"
    #     ).fetchall()
    #     conn.close()
    #     st.dataframe(evidence)



    elif menu == "Case Management":
        st.title("📁 Case Management")
        st.subheader("Create Investigation")
        case_id = st.text_input("Case ID")
        case_name = st.text_input("Case Name")
        description = st.text_area("Description")
        priority = st.selectbox(
            "Priority",
            [
                "Low",
                "Medium",
                "High",
                "Critical"
            ]
        )

        if st.button("Create Case"):
            create_case(
                case_id,
                case_name,
                description,
                st.session_state.username,
                priority
            )
            st.success("Case Created")

        st.divider()
        st.subheader("Existing Cases")
        cases = get_cases()
        import pandas as pd
        df = pd.DataFrame(
            cases,
            columns=[
                "ID",
                "Case ID",
                "Case Name",
                "Description",
                "Investigator",
                "Priority",
                "Status",
                "Created"
            ]
        )
        search = st.text_input(
            "🔍 Search Cases"
        )
        if search:
            df = df[
                df["Case Name"].str.contains(
                    search,
                    case=False
                ) |
                df["Case ID"].str.contains(
                    search,
                    case=False
                )
            ]
        
        priority_filter = st.selectbox(
            "Priority",
            [
                "All",
                "Low",
                "Medium",
                "High",
                "Critical"
            ]
        )
        if priority_filter != "All":
            df = df[
                df["Priority"] == priority_filter
            ]
        
        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "Open",
                "Closed"
            ]
        )
        if status_filter != "All":
            df = df[
                df["Status"] == status_filter
            ]


        st.dataframe(
            df,
            use_container_width=True
        )

        st.divider()
        st.subheader("Open Investigation")
        cases = get_cases()
        selected_case = st.selectbox(
            "Choose Case",
            cases,
            format_func=lambda x: f"{x[1]} - {x[2]}"
        )
        case = get_case(selected_case[1])
        alerts = get_case_alerts(case[1])
        evidence = get_case_evidence(case[1])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "📂 Evidence",
            len(evidence)
        )
        c2.metric(
            "🚨 Alerts",
            alerts
        )
        c3.metric(
            "⚠ Priority",
            case[5]
        )
        c4.metric(
            "📌 Status",
            case[6]
        )
        if case[6] == "Open":
            st.success("🟢 Investigation Status : OPEN")
        else:
            st.error("🔴 Investigation Status : CLOSED")

        priority = case[5]
        if priority == "Critical":
            st.error("🔥 Priority : CRITICAL")
        elif priority == "High":
            st.warning("⚠ Priority : HIGH")
        elif priority == "Medium":
            st.info("🔵 Priority : MEDIUM")
        else:
            st.success("🟢 Priority : LOW")
        st.subheader("Investigation Information")
        st.write("**Case ID:**", case[1])
        st.write("**Case Name:**", case[2])
        st.write("**Lead Investigator:**", case[4])
        st.write("**Description:**", case[3])
        st.write("**Created:**", case[7])
        # df = pd.DataFrame(
        #     evidence,
        #     columns=[
        #         "Evidence ID",
        #         "Title",
        #         "Filename",
        #         "Uploaded By",
        #         "Upload Time"
        #     ]
        # )
        # st.subheader("Evidence")
        # st.dataframe(
        #     df,
        #     use_container_width=True
        # )

        total, verified, tampered, alerts = get_case_statistics(case[1])
        st.subheader("📊 Investigation Summary")
        col1,col2,col3,col4 = st.columns(4)
        col1.metric(
            "📂 Evidence",
            total
        )
        col2.metric(
            "✅ Verified",
            verified
        )
        col3.metric(
            "🚨 Tampered",
            tampered
        )
        col4.metric(
            "⚠ Alerts",
            alerts
        )

        if total == 0:
            progress = 0
        else:
            progress = round(
                ((verified + tampered) / total) * 100
            )
        st.write("### Investigation Progress")
        st.progress(progress/100)
        st.write(f"**{progress}% of evidence has been examined.**")
        st.divider()
        st.subheader("✏ Edit Investigation")
        new_name = st.text_input(
            "Case Name",
            value=case[2],
            key="edit_case_name"
        )
        new_description = st.text_area(
            "Description",
            value=case[3],
            key="edit_case_description"
        )
        new_priority = st.selectbox(
            "Priority",
            ["Low","Medium","High","Critical"],
            index=["Low","Medium","High","Critical"].index(case[5]),
            key="edit_case_priority"
        )
        new_status = st.selectbox(
            "Status",
            ["Open","Closed"],
            index=["Open","Closed"].index(case[6]),
            key="edit_case_status"
        )
        if st.button("💾 Save Changes"):
            update_case(
                case[1],
                new_name,
                new_description,
                case[4],
                new_priority,
                new_status
            )
            st.success("Case Updated")
            st.rerun()

        st.divider()
        st.subheader("➕ Add Evidence to this Case")
        title = st.text_input(
            "Evidence Title",
            key="case_evidence_title"
        )
        uploaded_file = st.file_uploader(
            "Upload Evidence",
            key="case_upload"
        )
        if st.button("📤 Add Evidence"):
            if uploaded_file is None:
                st.warning("Please upload a file.")
            elif title == "":
                st.warning("Enter an evidence title.")
            else:
                file_hash = save_evidence(
                    case[1],
                    title,
                    uploaded_file,
                    st.session_state.username
                )
                st.success("Evidence Added Successfully!")
                st.code(file_hash)
                st.rerun()

        st.subheader("📂 Evidence in this Case")
        for item in evidence:
            with st.expander(f"📄 {item[1]}"):
                st.write("**Filename:**", item[2])
                st.write("**Uploaded By:**", item[3])
                st.write("**Uploaded On:**", item[4])
                # if st.button(
                #     "Open Evidence",
                #     key=f"open_{item[0]}"
                # ):
                #     st.session_state.selected_evidence = item[0]

            # stats = get_case_statistics(case[1])
            # col1, col2, col3 = st.columns(3)
            # col1.metric("📂 Evidence", stats["evidence"])
            # col2.metric("✅ Verified", stats["verified"])
            # col3.metric("🚨 Tampered", stats["tampered"])


        if st.session_state.role == "Admin":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Close Case"):
                    close_case(case[1])
                    st.success("Case Closed")
                    st.rerun()

            with col2:
                if st.button("🗑 Delete Case"):
                    delete_case(case[1])
                    st.success("Case Deleted")
                    st.rerun()

        if st.button("📄 Generate Case Report"):
            filename = f"{case[1]}_Report.pdf"
            generate_case_report(
                case[1],
                filename
            )
            with open(filename, "rb") as pdf:
                st.download_button(
                    "⬇ Download Report",
                    pdf,
                    file_name=filename,
                    mime="application/pdf"
                )

            


    # elif menu == "Tamper Alerts":
    #     conn = sqlite3.connect("forensic.db")
    #     alerts = pd.read_sql_query("""
    #     SELECT *
    #     FROM tamper_alerts
    #     ORDER BY detection_time DESC
    #     """, conn)
    #     conn.close()
    #     st.dataframe(
    #         alerts,
    #         use_container_width=True
    #     )



    elif menu == "Activity Monitoring":
        st.title("📊 Activity Monitoring")
        logs = get_audit_logs()
        col1,col2,col3 = st.columns(3)
        col1.metric(
            "📜 Total Activities",
            len(logs)
        )
        today = logs[
            logs["timestamp"].str.startswith(
                datetime.now().strftime("%Y-%m-%d")
            )
        ]
        col2.metric(
            "📅 Today's Activities",
            len(today)
        )
        col3.metric(
            "👥 Active Users",
            logs["username"].nunique()
        )
        users = ["All"] + get_users()
        selected_user = st.selectbox(
            "👤 User",
            users
        )
        actions = ["All"] + sorted(
            logs["action"].unique().tolist()
        )
        selected_action = st.selectbox(
            "⚙ Action",
            actions
        )
        search = st.text_input("🔍 Search Activity")
        filtered = logs.copy()
        if selected_user != "All":
            filtered = filtered[
                filtered["username"] == selected_user
            ]
        if selected_action != "All":
            filtered = filtered[
                filtered["action"] == selected_action
            ]
        if search:
            filtered = filtered[
                filtered["action"].str.contains(
                    search,
                    case=False
                )
            ]
        
        st.divider()
        for _, row in filtered.iterrows():
            action = row["action"]
            if "Tamper" in action:
                icon = "🚨"
            elif "Register" in action:
                icon = "📂"
            elif "Verify" in action:
                icon = "✅"
            elif "Metadata" in action:
                icon = "🧬"
            elif "Report" in action:
                icon = "📄"
            elif "Login" in action:
                icon = "🔑"
            else:
                icon = "📌"
            st.info(
                    f"""
            {icon} **{row['timestamp']}**
            👤 {row['username']}
            {row['action']}
            """
                )
            
        csv = filtered.to_csv(index=False).encode()
        st.download_button(
            "⬇ Export Activity Log",
            csv,
            "activity_logs.csv",
            "text/csv"
        )




    elif menu == "Evidence Search":

        st.header("Evidence Search Engine")

        search_term = st.text_input(
            "Search Evidence"
        )
        case_filter = st.text_input("Case ID")
        investigator_filter = st.text_input("Investigator")

        conn = sqlite3.connect("forensic.db")

        if search_term:

            query = """
            SELECT
            id,
            case_id,
            title,
            filename,
            uploaded_by,
            upload_time
            FROM evidence
            WHERE
            case_id LIKE ?
            OR title LIKE ?
            OR filename LIKE ?
            OR uploaded_by LIKE ?
            OR sha256 LIKE ?
            """

            values = (
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%"
            )

            results = conn.execute(
                query,
                values
            ).fetchall()

            if results:

                st.success(
                    f"{len(results)} result(s) found"
                )

                st.dataframe(results)

            else:

                st.warning(
                    "No matching evidence found"
                )

            log_action(
                st.session_state.username,
                f"Searched: {search_term}"
            )

        conn.close()




    elif menu == "Evidence Details":
        st.title("📂 Evidence Details")
        conn = sqlite3.connect("forensic.db")
        evidence_list = conn.execute("""
        SELECT id,title
        FROM evidence
        """).fetchall()
        conn.close()
        
        default_index = 0
        if "selected_evidence" in st.session_state:
            for i, item in enumerate(evidence_list):
                if item[0] == st.session_state.selected_evidence:
                    default_index = i
                    break

        selected = st.selectbox(
            "Select Evidence",
            evidence_list,
            index=default_index,
            format_func=lambda x: f"{x[0]} - {x[1]}"
        )

        evidence_id = selected[0]

        evidence, custody, verification, alerts = get_evidence_details(
            evidence_id
        )
        st.subheader("Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"""
        **Case ID**
        {evidence[1]}
        """)
            st.info(f"""
        **Title**
        {evidence[2]}
        """)
            st.info(f"""
        **Uploaded By**
        {evidence[7]}
        """)
        with col2:
            st.info(f"""
        **Upload Time**
        {evidence[8]}
        """)
            st.info(f"""
        **Filename**
        {evidence[3]}
        """)
            st.info(f"""
        **SHA256**
        `{evidence[6][:32]}...`
        """)
        col1,col2,col3,col4 = st.columns(4)
        col1.metric(
            "🔒 Encryption",
            "Enabled"
        )
        status = "Unknown"
        if not verification.empty:
            status = verification.iloc[0]["status"]
        col2.metric(
            "🔍 Status",
            status
        )
        col3.metric(
            "🚨 Alerts",
            len(alerts)
        )
        col4.metric(
            "📜 Custody",
            len(custody)
        )

        st.subheader("🖼 Evidence Preview")
        filepath = evidence[4]
        extension = filepath.split(".")[-1].lower()
        if extension in [
            "jpg",
            "jpeg",
            "png",
            "bmp",
            "gif"
        ]:
            st.image(filepath, width=500)

        elif extension in [
            "txt",
            "log",
            "csv"
        ]:
            with open(filepath) as f:
                st.code(f.read())
        
        elif extension == "pdf":
            with open(filepath, "rb") as pdf:
                st.download_button(
                    "Download PDF",
                    pdf,
                    file_name=evidence[3]
                )
        
        else:
            st.warning(
                "Preview not available for this file type."
            )

        st.subheader("📑 Chain of Custody")
        st.dataframe(custody)
        st.subheader("🚨 Tamper Alerts")
        st.dataframe(alerts)





    elif menu == "Secure Evidence Vault":

        st.header("Encrypted Evidence Vault")

        conn = sqlite3.connect("forensic.db")

        files = conn.execute("""
        SELECT id,title,encrypted_path
        FROM evidence
        """).fetchall()

        conn.close()

        st.dataframe(files)



    elif menu == "Evidence Timeline":
        st.header("📜 Evidence Timeline")
        conn = sqlite3.connect("forensic.db")
        evidence = conn.execute("""
        SELECT id,title
        FROM evidence
        """).fetchall()
        conn.close()
        selected = st.selectbox(
            "Select Evidence",
            evidence,
            format_func=lambda x: f"{x[0]} - {x[1]}"
        )
        evidence_id = selected[0]
        timeline = get_timeline(evidence_id)
        st.divider()
        for _, row in timeline.iterrows():
            if row["color"] == "green":
                st.success(f"""
        ### {row['icon']} {row['event']}
        👤 **{row['user']}**
        🕒 **{row['time']}**
        """)
            elif row["color"] == "red":
                st.error(f"""
        ### {row['icon']} {row['event']}
        👤 **{row['user']}**
        🕒 **{row['time']}**
        """)
            elif row["color"] == "orange":
                st.warning(f"""
        ### {row['icon']} {row['event']}
        👤 **{row['user']}**
        🕒 **{row['time']}**
        """)
            else:
                st.info(f"""
        ### {row['icon']} {row['event']}
        👤 **{row['user']}**
        🕒 **{row['time']}**
        """)





    elif menu == "Chain of Custody":

        st.header("Chain of Custody")

        conn = sqlite3.connect("forensic.db")

        evidence = conn.execute(
            "SELECT id,title FROM evidence"
        ).fetchall()

        selected = st.selectbox(
            "Select Evidence",
            evidence,
            format_func=lambda x:
            f"{x[0]} - {x[1]}"
        )

        action = st.selectbox(
            "Action",
            [
                "Assigned to Analyst",
                "Transferred",
                "Analyzed",
                "Archived"
            ]
        )

        if st.button("Add Custody Record"):

            conn.execute("""
            INSERT INTO custody(
            evidence_id,
            action,
            person,
            timestamp
            )
            VALUES(?,?,?,?)
            """,
            (
                selected[0],
                action,
                st.session_state.username,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ))

            conn.commit()

            st.success("Custody Updated")

        records = conn.execute("""
        SELECT *
        FROM custody
        ORDER BY timestamp DESC
        """).fetchall()

        st.dataframe(records)

        conn.close()    




    elif menu == "Generate Report":

        st.header("Forensic Report Generator")

        conn = sqlite3.connect("forensic.db")

        evidence_list = conn.execute("""
        SELECT *
        FROM evidence
        """).fetchall()

        selected = st.selectbox(
            "Select Evidence",
            evidence_list,
            format_func=lambda x:
            f"{x[0]} - {x[2]}"
        )

        if st.button("Generate PDF Report"):

            evidence_id = selected[0]

            custody_records = conn.execute("""
            SELECT *
            FROM custody
            WHERE evidence_id=?
            """,
            (evidence_id,)
            ).fetchall()

            report_path = (
                f"reports/report_{evidence_id}.pdf"
            )

            generate_report(
                report_path,
                selected,
                custody_records
            )

            with open(
                report_path,
                "rb"
            ) as pdf_file:

                st.download_button(
                    "Download Report",
                    pdf_file,
                    file_name=
                    f"report_{evidence_id}.pdf"
                )

            log_action(
                st.session_state.username,
                f"Generated Report {evidence_id}"
            )

        conn.close()



    elif menu == "Verify Evidence":

        if st.session_state.role not in [
            "Admin",
            "Analyst"
        ]:
            st.error("Access Denied")
            st.stop()

        st.header("Evidence Integrity Verification")

        conn = sqlite3.connect("forensic.db")

        evidence_list = conn.execute("""
        SELECT id,title,filepath,sha256
        FROM evidence
        """).fetchall()

        conn.close()

        selected = st.selectbox(
            "Select Evidence",
            evidence_list,
            format_func=lambda x:
            f"{x[0]} - {x[1]}"
        )

        if st.button("Verify Evidence"):

            evidence_id = selected[0]
            filepath = selected[2]
            stored_hash = selected[3]

            current_hash = calculate_hash(filepath)

            if current_hash == stored_hash:
                save_verification(
                    evidence_id,
                    st.session_state.username,
                    "Verified"
                )

                st.success(
                    "Integrity Verified"
                )

            else:
                title = selected[1]
                create_alert(
                    evidence_id,
                    title,
                    st.session_state.username,
                    stored_hash,
                    current_hash
                )
                # st.success("Alert inserted into database.")

                save_verification(
                    evidence_id,
                    st.session_state.username,
                    "Tampered"
                )

                st.error("⚠ Evidence Tampered!")
                log_action(
                    st.session_state.username,
                    f"Tamper detected: {title}"
                )


    elif menu == "Metadata Analysis":
        st.header("Metadata Analysis")

        conn = sqlite3.connect("forensic.db")

        evidence = conn.execute("""
        SELECT id,title,filepath
        FROM evidence
        """).fetchall()

        conn.close()

        selected = st.selectbox(
            "Select Evidence",
            evidence,
            format_func=lambda x:
            f"{x[0]} - {x[1]}"
        )

        if st.button("Extract Metadata"):

            filepath = selected[2]

            extension = filepath.split(".")[-1].lower()

            if extension in ["jpg", "jpeg", "png", "bmp", "gif"]:
                metadata = extract_image_metadata(filepath)

            elif extension == "pdf":
                metadata = extract_pdf_metadata(filepath)

            else:
                metadata = {
                    "Message": "Metadata extraction not supported."
                }

            log_action(
                st.session_state.username,
                f"Metadata Viewed: {selected[1]}"
            )

            metadata_df = pd.DataFrame(
                list(metadata.items()),
                columns=["Property", "Value"]
            )

            st.dataframe(metadata_df)


    elif menu == "User Management":
        st.header("User Management")

        users = get_users()
        admins = sum(1 for u in users if u[2] == "Admin")
        analysts = sum(1 for u in users if u[2] == "Analyst")
        viewers = sum(1 for u in users if u[2] == "Viewer")
        investigator = sum(1 for u in users if u[2] == "Investigator")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👑 Admins", admins)
        col2.metric("🛡 Analysts", analysts)
        col3.metric("👀 Viewers", viewers)
        col4.metric("👥 Investigators", investigator)

        search = st.text_input(
            "🔍 Search User",
            placeholder="Enter username..."
        )

        for user in users:
            if search and search.lower() not in user[1].lower():
                continue
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3,2,2,2])
                c1.write(f"**{user[1]}**")
                roles = ["Viewer", "Analyst", "Investigator", "Admin"]
                current_role = user[2]
                if current_role not in roles:
                    current_role = "Viewer"  # default fallback
                new_role = c2.selectbox(
                    "Role",
                    roles,
                    index=roles.index(current_role),
                    key=f"role_{user[0]}"
                )
            if c3.button(
                "💾 Save",
                key=f"save_{user[0]}"
            ):
                update_role(
                    user[0],
                    new_role
                )
                st.success("Role Updated")
                st.rerun()

            if user[1] != st.session_state.username:
                if c4.button(
                    "🗑 Delete",
                    key=f"delete_{user[0]}"
                ):
                    delete_user(user[0])
                    st.success("User Deleted")
                    st.rerun()

            else:
                c4.info("Current User")


        st.divider()
        st.subheader("➕ Create New User")
        new_username = st.text_input(
            "New Username"
        )
        new_password = st.text_input(
            "New Password",
            type="password"
        )
        new_role = st.selectbox(
            "Role",
            [
                "Admin",
                "Investigator",
                "Analyst",
                "Viewer"
            ]
        )

        if st.button("Create User"):
            success = create_user(
                new_username,
                new_password,
                new_role
            )

            if success:
                log_action(
                    st.session_state.username,
                    f"Created User: {new_username}"
                )
                st.success(
                    "User Created Successfully"
                )

            else:
                st.error(
                    "Username already exists"
                )


        # conn = sqlite3.connect("forensic.db")

        # users = conn.execute("""
        # SELECT
        # id,
        # username,
        # role
        # FROM users
        # """).fetchall()

        # conn.close()

        # st.subheader("Existing Users")

        # for user in users:

        #     col1, col2, col3, col4 = st.columns(
        #         [1,3,3,2]
        #     )

        #     with col1:
        #         st.write(user[0])

        #     with col2:
        #         st.write(user[1])

        #     with col3:
        #         st.write(user[2])

        #     with col4:

        #         if user[1] != "admin":

        #             if st.button(
        #                 f"Delete",
        #                 key=f"delete_{user[0]}"
        #             ):

        #                 delete_user(user[0])

        #                 log_action(
        #                     st.session_state.username,
        #                     f"Deleted User: {user[1]}"
        #                 )

        #                 st.success(
        #                     "User Deleted"
        #                 )

        #                 st.rerun()




    elif menu == "Audit Logs":

        conn = sqlite3.connect("forensic.db")

        logs = conn.execute(
            "SELECT * FROM audit_logs ORDER BY id DESC"
        ).fetchall()

        conn.close()

        st.dataframe(logs)

    if st.sidebar.button("Logout"):

        log_action(
            st.session_state.username,
            "Logged Out"
        )

        st.session_state.logged_in = False
        st.rerun()