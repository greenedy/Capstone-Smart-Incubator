INSERT INTO `smartincubator`.`configurations`
(`name`,
`species`,
`temperature`,
`humidity`,
`duration`,
`notes`,
`created_on`,
`running`,
`startTime`,
`selected`)
VALUES
('Preconfiguration1',
'Config',
'50',
'50',
'30',
'Test',
'1753-01-01 00:00:00',
0,
null,
0)
,('Preconfiguration2',
'Config',
'50',
'50',
'30',
'Test',
'1753-01-01 00:00:00',
0,
null,
0)
,('Preconfiguration3',
'Config',
'50',
'50',
'30',
'Test',
'1753-01-01 00:00:00',
0,
null,
0
);


INSERT INTO `smartincubator`.`settings`
(`name`,
`value`,
`type`
)
VALUES
('receiveEmail',
'0',
'boolean')
,('email',
'',
'string')