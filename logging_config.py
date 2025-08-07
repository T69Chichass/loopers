"""
Logging configuration for the FastAPI application.
"""
import logging
import logging.config
import sys
from typing import Dict, Any
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    
    # Create logs directory if log file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Logging configuration
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "pinecone": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "openai": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sentence_transformers": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            }
        }
    }
    
    # Add file handler if log file is specified
    if log_file:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": log_file,
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5
        }
        
        # Add file handler to all loggers
        for logger_config in logging_config["loggers"].values():
            if "file" not in logger_config["handlers"]:
                logger_config["handlers"].append("file")
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)


class QueryLogger:
    """Custom logger for query processing with structured logging."""
    
    def __init__(self, name: str = "query_processor"):
        self.logger = logging.getLogger(name)
    
    def log_query_start(self, query_id: str, query: str, user_id: str = None):
        """Log query processing start."""
        extra_data = {
            "query_id": query_id,
            "query_length": len(query),
            "user_id": user_id,
            "event": "query_start"
        }
        self.logger.info(
            f"Starting query processing - ID: {query_id}",
            extra=extra_data
        )
    
    def log_query_embedding(self, query_id: str, embedding_time: float):
        """Log embedding generation."""
        extra_data = {
            "query_id": query_id,
            "embedding_time": embedding_time,
            "event": "embedding_generated"
        }
        self.logger.info(
            f"Embedding generated - ID: {query_id}, Time: {embedding_time:.3f}s",
            extra=extra_data
        )
    
    def log_vector_search(self, query_id: str, results_count: int, search_time: float):
        """Log vector search results."""
        extra_data = {
            "query_id": query_id,
            "results_count": results_count,
            "search_time": search_time,
            "event": "vector_search_completed"
        }
        self.logger.info(
            f"Vector search completed - ID: {query_id}, Results: {results_count}, Time: {search_time:.3f}s",
            extra=extra_data
        )
    
    def log_llm_request(self, query_id: str, prompt_length: int):
        """Log LLM request."""
        extra_data = {
            "query_id": query_id,
            "prompt_length": prompt_length,
            "event": "llm_request_sent"
        }
        self.logger.info(
            f"LLM request sent - ID: {query_id}, Prompt length: {prompt_length}",
            extra=extra_data
        )
    
    def log_llm_response(self, query_id: str, response_length: int, llm_time: float):
        """Log LLM response."""
        extra_data = {
            "query_id": query_id,
            "response_length": response_length,
            "llm_time": llm_time,
            "event": "llm_response_received"
        }
        self.logger.info(
            f"LLM response received - ID: {query_id}, Length: {response_length}, Time: {llm_time:.3f}s",
            extra=extra_data
        )
    
    def log_query_complete(self, query_id: str, total_time: float, success: bool):
        """Log query completion."""
        extra_data = {
            "query_id": query_id,
            "total_time": total_time,
            "success": success,
            "event": "query_completed"
        }
        if success:
            self.logger.info(
                f"Query completed successfully - ID: {query_id}, Total time: {total_time:.3f}s",
                extra=extra_data
            )
        else:
            self.logger.error(
                f"Query failed - ID: {query_id}, Total time: {total_time:.3f}s",
                extra=extra_data
            )
    
    def log_error(self, query_id: str, error: Exception, context: str = ""):
        """Log query processing error."""
        extra_data = {
            "query_id": query_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "event": "query_error"
        }
        self.logger.error(
            f"Query error - ID: {query_id}, Error: {error}",
            extra=extra_data,
            exc_info=True
        )
