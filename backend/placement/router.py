"""
Placement Simulation API Endpoints.
"""

from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()


class PlacementStartRequest(BaseModel):
    pass


class PlacementAnswerRequest(BaseModel):
    round_type: str
    answer: Any


class PlacementResponse(BaseModel):
    result: Dict[str, Any]


@router.post("/start", response_model=PlacementResponse)
async def start_placement(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Start a new placement simulation.
    """
    try:
        from placement.simulator import PlacementSimulator
        from memory.student_memory import StudentMemory

        memory = request.app.state.memory
        llm = request.app.state.llm
        simulator = PlacementSimulator(memory=memory, llm=llm)

        result = await simulator.start_simulation(student_id=user_id)
        return PlacementResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start placement: {str(e)}")


@router.get("/status", response_model=PlacementResponse)
async def get_placement_status(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Get the current placement simulation status.
    """
    try:
        memory = request.app.state.memory
        profile = memory.get_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Student not found")

        placement_history = profile.get("placement_history", [])
        return PlacementResponse(result={
            "student_id": user_id,
            "has_history": len(placement_history) > 0,
            "rounds_completed": len(placement_history),
            "placement_history": placement_history
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/current", response_model=PlacementResponse)
async def get_current_round(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Get the current placement round for a student.
    """
    try:
        from placement.planner import PlacementPlanner

        memory = request.app.state.memory
        planner = PlacementPlanner(memory)
        plan = planner.build_execution_plan(user_id)

        return PlacementResponse(result=plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current round: {str(e)}")


@router.post("/answer", response_model=PlacementResponse)
async def submit_answer(
    request: Request,
    payload: PlacementAnswerRequest,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Submit an answer for the current placement round.
    """
    try:
        from placement.simulator import PlacementSimulator

        memory = request.app.state.memory
        llm = request.app.state.llm
        simulator = PlacementSimulator(memory=memory, llm=llm)

        result = await simulator.submit_answer(
            student_id=user_id,
            round_type=payload.round_type,
            answer=payload.answer
        )
        return PlacementResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")


@router.post("/end", response_model=PlacementResponse)
async def end_placement(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    End the placement simulation and generate the final report.
    """
    try:
        from placement.simulator import PlacementSimulator

        memory = request.app.state.memory
        llm = request.app.state.llm
        simulator = PlacementSimulator(memory=memory, llm=llm)

        result = await simulator.end_simulation(student_id=user_id)
        return PlacementResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end placement: {str(e)}")


@router.get("/report", response_model=PlacementResponse)
async def get_placement_report(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Get the placement report for a student.
    """
    try:
        from placement.report.generator import PlacementReportGenerator

        memory = request.app.state.memory
        llm = request.app.state.llm
        generator = PlacementReportGenerator(memory=memory, llm=llm)

        result = await generator.generate(student_id=user_id)
        return PlacementResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")
