from fastapi import APIRouter, HTTPException, status
from src.matching import services
from src.matching.schemas import MatchingSchema
from db import connectToDB
import json

router = APIRouter()


@router.post("/analyse")
async def analyse_matching(matching_data: MatchingSchema):
    cursor = connectToDB()
    
    if cursor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error connecting to the Database"
        )
        
    insert_query = '''
        INSERT INTO candidate_job_analysis (
            candidate_id, 
            job_id, 
            certificate, 
            degree, 
            experience, 
            responsibility, 
            technical_skill, 
            soft_skill,
            summary_comment,
            score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    result = services.analyse_matching(matching_data=matching_data)
    
    candidate_id = int(matching_data.candidate["candidate_id"])  # Convert to integer
    job_id = int(matching_data.job["job_id"])  # Convert to integer
    certificate = json.dumps(result["certificate"])  # Stringify the JSON object
    degree = json.dumps(result["degree"])  # Stringify the JSON object
    experience = json.dumps(result["experience"])  # Stringify the JSON object
    responsibility = json.dumps(result["responsibility"])  # Stringify the JSON object
    technical_skill = json.dumps(result["technical_skill"])  # Stringify the JSON object
    soft_skill = json.dumps(result["soft_skill"])  # Stringify the JSON object
    summary_comment = result["summary_comment"]  # Regular string
    score = result["score"]  # Numeric value
    
    try:
        # Execute the query with the actual data
        cursor.execute(insert_query, (
            candidate_id,
            job_id,
            certificate,
            degree,
            experience,
            responsibility,
            technical_skill,
            soft_skill,
            summary_comment,
            score
        ))

        # Commit the transaction
        cursor.commit()
        
        return "View Candidate to see more detail"
    
    except Exception as e:
        # Rollback the transaction in case of error
        cursor.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while inserting data into the database: {str(e)}"
        )
    
    finally:
        # Close the cursor and connection
        cursor.close()

@router.get("/get_matchings/{job_id}")
async def get_matching_analysis_by_job_id(job_id: int):
    # Connect to the database
    cursor = connectToDB()
    if cursor is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the Database"
        )

    # SQL query to fetch candidate job analysis by job_id
    select_query = '''
        SELECT candidate_id, job_id, certificate, degree, experience, responsibility, technical_skill, soft_skill, summary_comment, score
        FROM candidate_job_analysis
        WHERE job_id = ?
    '''

    try:
        # Execute the query
        cursor.execute(select_query, (job_id,))
        
        # Fetch all matching rows
        analysis_data = cursor.fetchall()
        
        # If no data found, raise an error
        if not analysis_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No matching analysis found for job_id {job_id}"
            )
        
        # Prepare the response by looping over all the results and formatting them
        analysis_list = []
        for row in analysis_data:
            analysis = {
                "candidate_id": row[0],
                "job_id": row[1],
                "certificate": json.loads(row[2]) if row[2] else {},
                "degree": json.loads(row[3]) if row[3] else {},
                "experience": json.loads(row[4]) if row[4] else {},
                "responsibility": json.loads(row[5]) if row[5] else {},
                "technical_skill": json.loads(row[6]) if row[6] else {},
                "soft_skill": json.loads(row[7]) if row[7] else {},
                "summary_comment": row[8],
                "score": row[9]
            }
            analysis_list.append(analysis)
        
        # Return the structured response as JSON
        return analysis_list

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching data: {str(e)}"
        )

    finally:
        # Close cursor and connection
        cursor.close()

@router.delete("/delete_matching")
async def delete_matching(job_id: int, candidate_id: int):
    # Connect to the database
    cursor = connectToDB()
    
    if cursor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error connecting to the Database"
        )

    # SQL query to delete the candidate_job_analysis entry based on job_id and candidate_id
    delete_query = '''
        DELETE FROM candidate_job_analysis
        WHERE job_id = ? AND candidate_id = ?
    '''

    try:
        # Execute the delete query
        cursor.execute(delete_query, (job_id, candidate_id))
        
        # Check if any row was affected
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analysis found for job_id {job_id} and candidate_id {candidate_id}"
            )
        
        # Commit the transaction
        cursor.commit()

        # Return success message
        return {"detail": f"Analysis for job_id {job_id} and candidate_id {candidate_id} deleted successfully."}
    
    except Exception as e:
        # Rollback the transaction in case of error
        cursor.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting data from the database: {str(e)}"
        )
    
    finally:
        # Close the cursor and connection
        cursor.close()