from fastapi import APIRouter, HTTPException, status
from src.job import services
from src.job.schemas import JobSchema
from db import connectToDB
import json

router = APIRouter()

@router.post("/analyse")
async def analyse_job(job_data: JobSchema):
    result = services.analyse_job(job_data=job_data)

    cursor = connectToDB()
    if cursor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error connecting to the Database"
        )
    
    insert_query = '''
        INSERT INTO job_descriptions (
            job_name, 
            certificate,
            degree, 
            experience,
            responsibility,
            soft_skill,
            technical_skill
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    
    job_name = job_data.job_name
    certificate = json.dumps(result["certificate"])  # Stringify the list
    degree = json.dumps(result["degree"])  # Stringify the list
    experience = json.dumps(result["experience"])  # Stringify the list
    responsibility = json.dumps(result["responsibility"])  # Stringify the list
    soft_skill = json.dumps(result["soft_skill"])  # Stringify the list
    technical_skill = json.dumps(result["technical_skill"])  # Stringify the list
    
    try:
        cursor.execute(insert_query, (
            job_name, 
            certificate,
            degree, 
            experience, 
            responsibility, 
            soft_skill, 
            technical_skill
        ))
        
        # Commit the transaction
        cursor.connection.commit()
    
    except Exception as e:
        # Rollback in case of error
        cursor.connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while inserting data into the database: {str(e)}"
        )
    
    finally:
        # Close the cursor/connection to prevent connection leakage
        cursor.close()

        
    return result


@router.get("/get_job/{job_id}")
async def get_job_description(job_id: int):
    # Connect to the database
    cursor = connectToDB()
    
    if cursor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error connecting to the Database"
        )

    # SQL query to fetch candidate profile by ID
    select_query = '''
        SELECT 
            job_name, 
            certificate,
            degree, 
            experience,
            responsibility,
            soft_skill,
            technical_skill
        FROM job_descriptions
        WHERE job_id = ?
    '''

    try:
        # Execute the query
        cursor.execute(select_query, (job_id,))
        
        # Fetch the data from the database
        job_data = cursor.fetchone()
        
        # If no data found, raise an error
        if job_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job description with id {job_id} not found"
            )
        
        # Map the result into a structured dictionary
        job_description = {
            "job_name": job_data[0],
            "certificate": json.loads(job_data[1]) if job_data[1] else [],  # Parse only if not NULL or empty
            "degree": json.loads(job_data[2]) if job_data[2] else [],  # Parse only if not NULL or empty
            "experience": json.loads(job_data[3]) if job_data[3] else [],  # Parse only if not NULL or empty
            "responsibility": json.loads(job_data[4]) if job_data[4] else [],  # Parse only if not NULL or empty
            "soft_skill": json.loads(job_data[5]) if job_data[5] else [],  # Parse only if not NULL or empty
            "technical_skill": json.loads(job_data[6]) if job_data[6] else [],  # Parse only if not NULL or empty
        }

        # Return the structured data as JSON response
        return job_description
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching data: {str(e)}"
        )
    
    finally:
        # Close cursor and connection to avoid leaks
        cursor.close()
        
        
@router.get("/get_all_jobs")
async def get_all_jobs():
    # Connect to the database
    cursor = connectToDB()
    if cursor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error connecting to the Database"
        )
    # SQL query to fetch all candidate profiles
    select_query = '''
        SELECT 
            job_id,
            job_name, 
            certificate,
            degree, 
            experience,
            responsibility,
            soft_skill,
            technical_skill
        FROM job_descriptions
    '''

    try:
        # Execute the query
        cursor.execute(select_query)
        
        # Fetch all the data from the database
        job_data = cursor.fetchall()

        # If no data is found, return an empty list
        if not job_data:
            return []

        # Map the result into a structured list of dictionaries
        jobs = []
        for row in job_data:
            job_description = {
                "job_id": row[0],
                "job_name": row[1],
                "certificate": json.loads(row[2]) if row[2] else [],  # Parse only if not NULL or empty
                "degree": json.loads(row[3]) if row[3] else [],  # Parse only if not NULL or empty
                "experience": json.loads(row[4]) if row[4] else [],  # Parse only if not NULL or empty
                "responsibility": json.loads(row[5]) if row[5] else [],  # Parse only if not NULL or empty
                "soft_skill": json.loads(row[6]) if row[6] else [],  # Parse only if not NULL or empty
                "technical_skill": json.loads(row[7]) if row[7] else [],  # Parse only if not NULL or empty
            }
            jobs.append(job_description)

        # Return the structured data as a list of JSON objects
        return jobs
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching data: {str(e)}"
        )
    
    finally:
        # Close cursor and connection to avoid leaks
        cursor.close()


@router.delete("/delete_job/{job_id}")
async def delete_job(job_id: int):
    # Connect to the database
    cursor = connectToDB()
    if cursor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error connecting to the Database"
        )

    # SQL query to delete the candidate profile by ID
    delete_query = '''
        DELETE FROM job_descriptions
        WHERE job_id = ?
    '''

    try:
        # Execute the deletion query
        cursor.execute(delete_query, (job_id,))
        
        # Check if any row was deleted
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Commit the transaction to reflect changes
        cursor.commit()

        return {"detail": "Job deleted successfully"}

    except Exception as e:
        # Rollback in case of error
        cursor.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the candidate: {str(e)}"
        )

    finally:
        # Close cursor and connection to avoid leaks
        cursor.close()
