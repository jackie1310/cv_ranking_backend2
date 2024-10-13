from fastapi import APIRouter, Body, HTTPException, status, UploadFile, File
from src.candidate import services
from db import connectToDB
import json

router = APIRouter()


# @router.post("/analyse", response_model=ResponseSchema)
@router.post("/analyse")
async def analyse_candidate_router(file: UploadFile = File(...)):
    # Save the uploaded file
    file_name = await services.save_cv_candidate(file=file)

    # Read the CV content
    cv_content = services.read_cv_candidate(file_name=file_name)

    # Analyse the candidate's CV
    result = services.analyse_candidate(cv_content=cv_content)

    # Connect to the database
    cursor = connectToDB()
    
    if cursor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error connecting to the Database"
        )

    # SQL query to insert candidate profile
    insert_query = '''
        INSERT INTO candidate_profiles (
            candidate_name, 
            phone_number, 
            email, 
            degree, 
            experience,
            technical_skill,
            responsibility,
            certificate,
            soft_skill,
            comment,
            job_recommended
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    # Extract values from the result dictionary
    candidate_name = result["candidate_name"]
    phone_number = result["phone_number"]
    email = result["email"]
    degree = json.dumps(result["degree"])  # Stringify the list
    experience = json.dumps(result["experience"])  # Stringify the list
    technical_skill = json.dumps(result["technical_skill"])  # Stringify the list
    responsibility = json.dumps(result["responsibility"])  # Stringify the list
    certificate = json.dumps(result["certificate"])  # Stringify the list
    soft_skill = json.dumps(result["soft_skill"])  # Stringify the list
    comment = result["comment"]
    job_recommended = json.dumps(result["job_recommended"])  # Stringify the list

    # Execute the query with the actual data
    try:
        cursor.execute(insert_query, (
            candidate_name, 
            phone_number, 
            email, 
            degree, 
            experience, 
            technical_skill, 
            responsibility, 
            certificate, 
            soft_skill, 
            comment, 
            job_recommended
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


@router.get("/get_candidate/{candidate_id}")
async def get_candidate_profile(candidate_id: int):
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
            candidate_name, 
            phone_number, 
            email, 
            degree, 
            experience,
            technical_skill,
            responsibility,
            certificate,
            soft_skill,
            comment,
            job_recommended
        FROM candidate_profiles
        WHERE candidate_id = ?
    '''

    try:
        # Execute the query
        cursor.execute(select_query, (candidate_id,))
        
        # Fetch the data from the database
        candidate_data = cursor.fetchone()
        
        # If no data found, raise an error
        if candidate_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with id {candidate_id} not found"
            )
        
        # Map the result into a structured dictionary
        candidate_profile = {
            "candidate_name": candidate_data[0],
            "phone_number": candidate_data[1],
            "email": candidate_data[2],
            "degree": json.loads(candidate_data[3]) if candidate_data[3] else [],  # Parse only if not NULL or empty
            "experience": json.loads(candidate_data[4]) if candidate_data[4] else [],  # Parse only if not NULL or empty
            "technical_skill": json.loads(candidate_data[5]) if candidate_data[5] else [],  # Parse only if not NULL or empty
            "responsibility": json.loads(candidate_data[6]) if candidate_data[6] else [],  # Parse only if not NULL or empty
            "certificate": json.loads(candidate_data[7]) if candidate_data[7] else [],  # Parse only if not NULL or empty
            "soft_skill": json.loads(candidate_data[8]) if candidate_data[8] else [],  # Parse only if not NULL or empty
            "comment": candidate_data[9],
            "job_recommended": json.loads(candidate_data[10]) if candidate_data[10] else []  # Part JSON string back to list
        }

        # Return the structured data as JSON response
        return candidate_profile
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching data: {str(e)}"
        )
    
    finally:
        # Close cursor and connection to avoid leaks
        cursor.close()

@router.get("/get_all_candidates")
async def get_all_candidate_profiles():
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
            candidate_id,
            candidate_name, 
            phone_number, 
            email, 
            degree, 
            experience,
            technical_skill,
            responsibility,
            certificate,
            soft_skill,
            comment,
            job_recommended
        FROM candidate_profiles
    '''

    try:
        # Execute the query
        cursor.execute(select_query)
        
        # Fetch all the data from the database
        candidate_data = cursor.fetchall()

        # If no data is found, return an empty list
        if not candidate_data:
            return []

        # Map the result into a structured list of dictionaries
        candidates = []
        for row in candidate_data:
            candidate_profile = {
                "candidate_id": row[0],
                "candidate_name": row[1],
                "phone_number": row[2],
                "email": row[3],
                "degree": json.loads(row[4]),  # Convert JSON string back to list
                "experience": json.loads(row[5]),  # Convert JSON string back to list
                "technical_skill": json.loads(row[6]),  # Convert JSON string back to list
                "responsibility": json.loads(row[7]),  # Convert JSON string back to list
                "certificate": json.loads(row[8]),  # Convert JSON string back to list
                "soft_skill": json.loads(row[9]),  # Convert JSON string back to list
                "comment": row[10],
                "job_recommended": json.loads(row[11])  # Convert JSON string back to list
            }
            candidates.append(candidate_profile)

        # Return the structured data as a list of JSON objects
        return candidates
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching data: {str(e)}"
        )
    
    finally:
        # Close cursor and connection to avoid leaks
        cursor.close()


@router.delete("/delete_candidate/{candidate_id}")
async def delete_candidate(candidate_id: int):
    # Connect to the database
    cursor = connectToDB()
    if cursor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error connecting to the Database"
        )

    # SQL query to delete the candidate profile by ID
    delete_query = '''
        DELETE FROM candidate_profiles
        WHERE candidate_id = ?
    '''

    try:
        # Execute the deletion query
        cursor.execute(delete_query, (candidate_id,))
        
        # Check if any row was deleted
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )

        # Commit the transaction to reflect changes
        cursor.commit()

        return {"detail": "Candidate deleted successfully"}

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
