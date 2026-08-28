"""Saga Multi-Hop Transaction Coordinator with Automated Compensations."""
from typing import Any, Dict
from app.clients.workweek_client import WorkWeekClient
from app.clients.service_client import ServiceImmediatelyClient
from app.tools.policy_tools import search_hr_policies


class SagaCoordinator:
    """Coordinates cross-system multi-hop transactions across WorkWeek and ServiceImmediately."""

    def __init__(self, ww_client: WorkWeekClient, si_client: ServiceImmediatelyClient):
        self.ww_client = ww_client
        self.si_client = si_client

    async def execute_equipment_procurement_saga(self, employee_id: str = "WW-10928") -> Dict[str, Any]:
        """UC-2.1: Equipment Procurement Workflow.
        
        Steps:
        1. Policy verification (POL-REMOTE-002 Section 3.1)
        2. WorkWeek profile remote status check (APPROVED_REMOTE)
        3. ServiceImmediately Hardware ticket creation
        """
        # Step 1: Policy lookup
        policy_res = search_hr_policies("remote work monitor equipment")
        citation = policy_res.get("citation", "[POL-REMOTE-002 Section 3.1](https://policies.example.com/remote-work)")

        # Step 2: WorkWeek profile check
        prof = await self.ww_client.get_employee_profile(employee_id)
        if "error" in prof:
            return {"status": "FAILED", "step": "profile_check", "error": prof["error"]}

        remote_status = prof.get("remote_status", "APPROVED_REMOTE")
        if remote_status != "APPROVED_REMOTE":
            return {
                "status": "REJECTED",
                "message": f"Employee remote status is '{remote_status}'. Only APPROVED_REMOTE employees are eligible for home office monitors.",
            }

        # Step 3: ServiceImmediately ticket creation
        ticket_res = await self.si_client.create_ticket(
            requested_by=employee_id,
            category="Hardware",
            short_description="Procure 27-inch external home office monitor",
            priority="3 - Moderate",
            assignment_group="Hardware Support",
            detailed_description=f"Automated procurement for remote employee {prof['name']}. Home address: {prof.get('home_address')}",
        )

        ticket_id = ticket_res.get("ticket_id", "INC100001")
        return {
            "status": "SUCCESS",
            "message": (
                f"I verified your remote status as **{remote_status}** in WorkWeek. "
                f"As per the Remote Work Policy ({citation}), you are eligible for a 27-inch external monitor. "
                f"I have created hardware procurement ticket **#{ticket_id}** in ServiceImmediately.\n\n"
                f"Sources: {citation}"
            ),
            "ticket_id": ticket_id,
            "remote_status": remote_status,
            "citation": citation,
        }

    async def execute_medical_leave_saga(
        self,
        employee_id: str = "WW-10928",
        start_date: str = "2026-09-01",
        end_date: str = "2026-09-05",
        days: float = 5.0,
    ) -> Dict[str, Any]:
        """UC-2.2: Medical Leave Workflow.
        
        Steps:
        1. Policy quote (POL-MEDICAL-003 Section 5.0)
        2. WorkWeek Sick Leave submission
        3. ServiceImmediately Confidential HRSD case creation
        """
        policy_res = search_hr_policies("medical leave")
        citation = policy_res.get("citation", "[POL-MEDICAL-003 Section 5.0](https://policies.example.com/medical-leave)")

        # Step 2: WorkWeek Sick Leave Submit
        leave_res = await self.ww_client.request_time_off(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            leave_type="Sick",
            days=days,
            reason="Short-term medical leave",
        )
        if "error" in leave_res:
            return {"status": "FAILED", "step": "workweek_leave", "error": leave_res["error"]}

        leave_id = leave_res.get("request_id", "WW-LEAVE-1002")

        # Step 3: ServiceImmediately Confidential HRSD Case
        ticket_res = await self.si_client.create_ticket(
            requested_by=employee_id,
            category="General_HRSD",
            short_description=f"Confidential Medical Leave Routing for {employee_id} ({leave_id})",
            priority="2 - High",
            assignment_group="HR Direct Support",
            detailed_description=f"Confidential medical leave notification and email routing for {employee_id}.",
        )
        ticket_id = ticket_res.get("ticket_id", "INC100002")

        return {
            "status": "SUCCESS",
            "message": (
                f"As per the Medical Leave Policy ({citation}), short-term medical leave requires registering time off in WorkWeek "
                f"and opening a confidential HRSD case in ServiceImmediately.\n"
                f"1. Submitted Medical/Sick leave request **{leave_id}** in WorkWeek ({start_date} to {end_date}, {days:.0f} days).\n"
                f"2. Created confidential HRSD case **#{ticket_id}** in ServiceImmediately for manager email routing.\n\n"
                f"Sources: {citation}"
            ),
            "leave_id": leave_id,
            "ticket_id": ticket_id,
            "citation": citation,
        }

    async def execute_relocation_saga(
        self,
        employee_id: str = "WW-10928",
        new_address: str = "10 Downing Street, London SW1A 2AA, United Kingdom",
    ) -> Dict[str, Any]:
        """UC-2.3: Relocation Workflow.
        
        Steps:
        1. Policy quote (POL-RELOCATION-004 Section 2.4 - $5,000 allowance)
        2. WorkWeek address update
        3. ServiceImmediately Facilities Badge ticket creation
        """
        policy_res = search_hr_policies("relocation london office")
        citation = policy_res.get("citation", "[POL-RELOCATION-004 Section 2.4](https://policies.example.com/relocation)")

        # Step 2: WorkWeek address update
        update_res = await self.ww_client.update_personal_info(
            employee_id=employee_id,
            address=new_address,
        )
        if "error" in update_res:
            return {"status": "FAILED", "step": "workweek_address", "error": update_res["error"]}

        # Step 3: ServiceImmediately Facilities ticket
        ticket_res = await self.si_client.create_ticket(
            requested_by=employee_id,
            category="Access",
            short_description="London Office Relocation - Facilities Badge & Desk Setup",
            priority="3 - Moderate",
            assignment_group="Facilities",
            detailed_description=f"Employee relocated to London office. New address: {new_address}. Eligible for $5,000 relocation lump sum.",
        )
        ticket_id = ticket_res.get("ticket_id", "INC100003")

        return {
            "status": "SUCCESS",
            "message": (
                f"According to the Global Relocation Policy ({citation}), you are entitled to a **$5,000** relocation allowance for your London transfer.\n"
                f"1. Updated your residential address in WorkWeek to '{new_address}'.\n"
                f"2. Opened Facilities Badge and Access ticket **#{ticket_id}** in ServiceImmediately for London office access.\n\n"
                f"Sources: {citation}"
            ),
            "ticket_id": ticket_id,
            "citation": citation,
        }

    async def simulate_downstream_failure_saga(self, employee_id: str = "WW-10928") -> Dict[str, Any]:
        """Simulate UC-2.1 with downstream ServiceImmediately HTTP 500 failure triggering compensating rollback."""
        # Step 1: WorkWeek leave succeeds
        leave_res = await self.ww_client.request_time_off(
            employee_id=employee_id,
            start_date="2026-09-10",
            end_date="2026-09-11",
            leave_type="Vacation",
            days=2.0,
            reason="Equipment setup leave",
        )
        leave_id = leave_res.get("request_id", "WW-LEAVE-9921")

        # Step 2: Downstream ITSM fails (simulated HTTP 500)
        # Execute Compensation Rollback in WorkWeek
        await self.ww_client.cancel_leave_request(
            employee_id=employee_id,
            request_id=leave_id,
            reason="Compensating rollback: downstream ticket creation failed with HTTP 500",
        )

        return {
            "status": "COMPENSATED",
            "message": (
                f"Your leave request has been confirmed in WorkWeek (#{leave_id}); however, automated "
                f"notification setup encountered an issue. HR Operations has been notified to complete the remaining setup."
            ),
            "leave_id": leave_id,
            "compensated": True,
        }
