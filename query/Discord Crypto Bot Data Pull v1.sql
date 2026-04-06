with 

base as (

  select 
    timestamp
    , current_price
    , currency
    , crypto_id
    , batch_id
    , min(current_price) over(partition by crypto_id, currency) lowest_30_day
    , max(current_price) over(partition by crypto_id, currency) highest_30_day
    , row_number() over(partition by crypto_id order by timestamp desc) rn
  from `testing.raw_daily_data`
  where 1=1 
    and currency = 'idr'
    and date(timestamp) >= date_sub(current_date('Asia/Jakarta'), interval 30 day)

)

, fin as ( 

  select 

    timestamp
    , crypto_id
    , currency
    , current_price
    , case 
        when current_price = lowest_30_day then 1 
        else 0
      end is_lowest_30_day
    , case 
        when current_price = highest_30_day then 1
        else 0
      end is_highest_30_day
    , case 
        when date(timestamp) = current_date('Asia/Jakarta') then 'current_day_data'
        when date(timestamp) != current_date('Asia/Jakarta') then 'not_current_day_data'
      end is_data_current_day
  from base
  where 1=1 
    and rn = 1


)

select * from fin
where 1=1 