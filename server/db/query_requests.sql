SELECT
    url.url_id as url_id,
    owner.first_name as owner_first_name,
    owner.last_name as owner_last_name,
    owner.department as owner_department,
    requester.first_name as requester_first_name,
    requester.last_name as requester_last_name,
    DATE_FORMAT(url.url_request_timestamp, '%Y-%m-%d %H:%i:%S') as url_request_timestamp,
    url.short_url as short_url,
    url.orig_url as orig_url,
    url.status as status
FROM
    urls as url
INNER JOIN
    users as owner on url.owner_id=owner.user_id
INNER JOIN
    users as requester on url.requester_id=requester.user_id;
