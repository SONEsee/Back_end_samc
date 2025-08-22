from django.db import connection
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AssetService:
    """Service class ສຳລັບເອີ້ນ stored procedure"""
    
    @staticmethod
    def get_asset_list_by_criteria(
        asset_type_id: Optional[str] = None,
        asset_status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        ເອີ້ນ stored procedure Asset_List_GetAllList_ByAsset_Status_ByDate
        
        Args:
            asset_type_id: Asset type ID
            asset_status: Asset status  
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of dictionaries containing asset data
        """
        try:
            with connection.cursor() as cursor:
                # Execute stored procedure
                cursor.execute(
                    """
                    EXEC Asset_List_GetAllList_ByAsset_Status_ByDate 
                    @asset_type_id = %s,
                    @asset_status = %s, 
                    @startDate = %s,
                    @Enddate = %s
                    """,
                    [asset_type_id, asset_status, start_date, end_date]
                )
                
                # Get column names
                columns = [col[0] for col in cursor.description]
                
                # Convert to list of dictionaries
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                    
                logger.info(f"Retrieved {len(results)} assets with criteria: "
                           f"type_id={asset_type_id}, status={asset_status}")
                
                return results
                
        except Exception as e:
            logger.error(f"Error calling stored procedure: {str(e)}")
            raise

    @staticmethod
    def get_asset_summary_stats(
        asset_type_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        ສ້າງສະຖິຕິສະຫຼຸບຂອງ assets
        """
        try:
            assets = AssetService.get_asset_list_by_criteria(
                asset_type_id=asset_type_id,
                start_date=start_date, 
                end_date=end_date
            )
            
            
            status_counts = {}
            type_counts = {}
            
            for asset in assets:
                
                status = asset.get('asset_status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                
                asset_type = asset.get('asset_type_id_id', 'Unknown')
                type_counts[asset_type] = type_counts.get(asset_type, 0) + 1
            
            return {
                'total_count': len(assets),
                'status_breakdown': status_counts,
                'type_breakdown': type_counts,
                'raw_data': assets
            }
            
        except Exception as e:
            logger.error(f"Error generating asset summary: {str(e)}")
            raise