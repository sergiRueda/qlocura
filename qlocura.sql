-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 06-06-2025 a las 21:36:23
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `qlocura`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('24595ca3eaac');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedido`
--

CREATE TABLE `pedido` (
  `id` int(11) NOT NULL,
  `fecha` datetime DEFAULT NULL,
  `usuario_id` int(11) NOT NULL,
  `domiciliario_id` int(11) DEFAULT NULL,
  `ubicacion` varchar(255) DEFAULT NULL,
  `metodo_pago` enum('EFECTIVO','NEQUI','DAVIPLATA') DEFAULT NULL,
  `precio_total` float NOT NULL,
  `estado_pedido` enum('PENDIENTE','EN_CAMINO','ENTREGADO') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedido`
--

INSERT INTO `pedido` (`id`, `fecha`, `usuario_id`, `domiciliario_id`, `ubicacion`, `metodo_pago`, `precio_total`, `estado_pedido`) VALUES
(1, '2025-06-06 03:17:56', 3, 2, 'Calle 108 sur N°7-39', 'NEQUI', 40000, 'ENTREGADO'),
(2, '2025-06-06 07:19:20', 3, 2, 'Calle 109 sur N° 9-54', 'EFECTIVO', 16000, 'ENTREGADO'),
(3, '2025-06-06 07:19:57', 3, 2, 'Calle 109 sur N°9-54', 'NEQUI', 3000, 'ENTREGADO'),
(4, '2025-06-06 07:35:56', 3, 2, 'Calle 108 sur N°7-39', 'EFECTIVO', 21000, 'EN_CAMINO');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedido_detalle`
--

CREATE TABLE `pedido_detalle` (
  `id` int(11) NOT NULL,
  `pedido_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedido_detalle`
--

INSERT INTO `pedido_detalle` (`id`, `pedido_id`, `producto_id`, `cantidad`, `precio_unitario`) VALUES
(1, 1, 1, 1, 16000),
(2, 1, 2, 1, 18000),
(3, 1, 3, 2, 3000),
(4, 2, 1, 1, 16000),
(5, 3, 3, 1, 3000),
(6, 4, 2, 1, 18000),
(7, 4, 3, 1, 3000);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `precio` float NOT NULL,
  `categoria` varchar(50) NOT NULL,
  `foto_url` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id`, `nombre`, `precio`, `categoria`, `foto_url`) VALUES
(1, 'Hamburguesa doble ', 16000, 'Comida Rápida', 'https://st.depositphotos.com/1884173/2999/i/450/depositphotos_29998659-stock-photo-classic-burgers.jpg'),
(2, 'Salchipapa Especial', 18000, 'Comida Rápida', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3HqatXBM4lS0hJGVKXUZaTdSGtDJ09AvQ9g&s'),
(3, 'Canada Dry', 3000, 'Bebida', 'https://walmartcr.vtexassets.com/arquivos/ids/463826/Gaseosa-Canada-Dry-Ginger-Ale-regular-lata-355-ml-1-26340.jpg?v=638328300047730000');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte_pedido`
--

CREATE TABLE `reporte_pedido` (
  `id` int(11) NOT NULL,
  `hora_salida` time NOT NULL,
  `hora_llegada` time NOT NULL,
  `precio_total` float NOT NULL,
  `pedido_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `nombre` enum('CLIENTE','DOMICILIARIO','ADMINISTRADOR') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id`, `nombre`) VALUES
(1, 'CLIENTE'),
(2, 'DOMICILIARIO'),
(3, 'ADMINISTRADOR');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `contrasena_hash` varchar(255) NOT NULL,
  `rol_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre`, `email`, `contrasena_hash`, `rol_id`) VALUES
(1, 'Administrador', 'admin@qlocura.com', 'scrypt:32768:8:1$Qlhm2WrjyJGZpO0J$0abf530a47e9c842e3f79bf2452ea3670a1cac2ee642973cab7b6e1e955d423458ae8adc20fac0e9371531a936635ce4caca85c7a17178a305eeeff7b87f2ed2', 3),
(2, 'Camilo Galeano', 'camilo@gmail.com', 'scrypt:32768:8:1$NPT4ehF06Cu19Wgq$d2c67b67ffd7112a4d1dc32f5e26dbab307843e0457d2e7603a8df587d2d9273ca53a43501907b4642bd31497d5a4c795b862a0179c8d2da911b7e317f58f5b5', 2),
(3, 'Andrey Fontecha', 'andrey1@gmail.com', 'scrypt:32768:8:1$iD89BrB64tGV4LB0$9e4b5d86ff10042bc6fa5b7f0440c4f8b683d8448592f32e58b2d6b783c29ecad46d1766c08cede86410dc8c615e61f781b068d2b4ef36eff6caa44407abf8f8', 1);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indices de la tabla `pedido`
--
ALTER TABLE `pedido`
  ADD PRIMARY KEY (`id`),
  ADD KEY `domiciliario_id` (`domiciliario_id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `pedido_detalle`
--
ALTER TABLE `pedido_detalle`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pedido_id` (`pedido_id`),
  ADD KEY `producto_id` (`producto_id`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `reporte_pedido`
--
ALTER TABLE `reporte_pedido`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pedido_id` (`pedido_id`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `rol_id` (`rol_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `pedido`
--
ALTER TABLE `pedido`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `pedido_detalle`
--
ALTER TABLE `pedido_detalle`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `reporte_pedido`
--
ALTER TABLE `reporte_pedido`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `pedido`
--
ALTER TABLE `pedido`
  ADD CONSTRAINT `pedido_ibfk_1` FOREIGN KEY (`domiciliario_id`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `pedido_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `pedido_detalle`
--
ALTER TABLE `pedido_detalle`
  ADD CONSTRAINT `pedido_detalle_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `pedido` (`id`),
  ADD CONSTRAINT `pedido_detalle_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`);

--
-- Filtros para la tabla `reporte_pedido`
--
ALTER TABLE `reporte_pedido`
  ADD CONSTRAINT `reporte_pedido_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `pedido` (`id`);

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

/*consultas*/

-- Obtener todos los productos
SELECT * FROM productos;

-- Ver todos los usuarios con su rol
SELECT u.id, u.nombre, r.nombre AS rol
FROM usuarios u
JOIN roles r ON u.rol_id = r.id;

-- Listar todos los pedidos ordenados por fecha descendente
SELECT * FROM pedido ORDER BY fecha DESC;


-- Obtener detalles de cada pedido con nombre del producto y usuario
SELECT p.id AS pedido_id, u.nombre AS cliente, pr.nombre AS producto, pd.cantidad, pd.precio_unitario
FROM pedido p
INNER JOIN usuarios u ON p.usuario_id = u.id
INNER JOIN pedido_detalle pd ON pd.pedido_id = p.id
INNER JOIN productos pr ON pr.id = pd.producto_id;

-- Obtener nombre del domiciliario y sus pedidos
SELECT p.id AS pedido_id, u.nombre AS domiciliario, p.estado_pedido
FROM pedido p
INNER JOIN usuarios u ON p.domiciliario_id = u.id;


-- Listar todos los pedidos y mostrar domiciliario (incluso si no tiene)
SELECT p.id, p.fecha, u1.nombre AS cliente, u2.nombre AS domiciliario
FROM pedido p
LEFT JOIN usuarios u1 ON p.usuario_id = u1.id
LEFT JOIN usuarios u2 ON p.domiciliario_id = u2.id;

-- Mostrar todos los usuarios aunque no tengan rol
SELECT u.id, u.nombre, r.nombre AS rol
FROM usuarios u
LEFT JOIN roles r ON u.rol_id = r.id;


-- Mostrar todos los roles incluso si no tienen usuarios
SELECT r.nombre AS rol, u.nombre AS usuario
FROM usuarios u
RIGHT JOIN roles r ON u.rol_id = r.id;


-- Obtener productos que han sido pedidos al menos una vez
SELECT * FROM productos
WHERE id IN (
  SELECT DISTINCT producto_id FROM pedido_detalle
);

-- Usuarios que han hecho más de un pedido
SELECT nombre, id FROM usuarios
WHERE id IN (
  SELECT usuario_id FROM pedido
  GROUP BY usuario_id HAVING COUNT(*) > 1
);


-- Total de pedidos por estado
SELECT estado_pedido, COUNT(*) AS cantidad
FROM pedido
GROUP BY estado_pedido;

-- Total vendido por producto
SELECT pr.nombre, SUM(pd.cantidad * pd.precio_unitario) AS total_vendido
FROM pedido_detalle pd
JOIN productos pr ON pd.producto_id = pr.id
GROUP BY pr.nombre;

-- Total vendido por cliente
SELECT u.nombre AS cliente, SUM(p.precio_total) AS total_comprado
FROM pedido p
JOIN usuarios u ON p.usuario_id = u.id
GROUP BY u.nombre;


-- Reporte completo de pedidos: cliente, domiciliario, productos, cantidades, precio total
SELECT 
  p.id AS pedido_id,
  u1.nombre AS cliente,
  u2.nombre AS domiciliario,
  pr.nombre AS producto,
  pd.cantidad,
  pd.precio_unitario,
  p.precio_total,
  p.estado_pedido
FROM pedido p
JOIN usuarios u1 ON p.usuario_id = u1.id
LEFT JOIN usuarios u2 ON p.domiciliario_id = u2.id
JOIN pedido_detalle pd ON p.id = pd.pedido_id
JOIN productos pr ON pd.producto_id = pr.id
ORDER BY p.id;


-- Mostrar estado de pedidos en texto descriptivo
SELECT id,
      CASE estado_pedido
        WHEN 'PENDIENTE' THEN 'Aún no se ha entregado'
        WHEN 'EN_CAMINO' THEN 'El pedido va en camino'
        WHEN 'ENTREGADO' THEN 'El pedido fue entregado'
      END AS estado_descriptivo
FROM pedido;


-- Pedidos realizados en el último día
SELECT * FROM pedido
WHERE fecha >= NOW() - INTERVAL 1 DAY;

-- Diferencia entre hora salida y llegada (cuando haya datos en reporte_pedido)
SELECT rp.id, rp.hora_salida, rp.hora_llegada,
      TIMEDIFF(rp.hora_llegada, rp.hora_salida) AS duracion_entrega
FROM reporte_pedido rp;


-- Facturación por método de pago
SELECT metodo_pago, SUM(precio_total) AS total
FROM pedido
GROUP BY metodo_pago;

-- Total de productos vendidos por categoría
SELECT pr.categoria, SUM(pd.cantidad) AS cantidad_vendida
FROM pedido_detalle pd
JOIN productos pr ON pr.id = pd.producto_id
GROUP BY pr.categoria;

-- Obtener nombres de usuarios y los productos que han comprado (con INNER JOIN)
SELECT u.nombre AS usuario, p.nombre AS producto
FROM usuarios u
INNER JOIN pedido pe ON u.id = pe.usuario_id
INNER JOIN pedido_detalle pd ON pe.id = pd.pedido_id
INNER JOIN productos p ON pd.producto_id = p.id;



-- Listar todos los usuarios y mostrar si tienen pedidos o no
SELECT u.nombre, pe.id AS pedido_id
FROM usuarios u
LEFT JOIN pedido pe ON u.id = pe.usuario_id;



-- Listar todos los productos y los pedidos en los que aparecen (aunque no haya pedidos asociados, con RIGHT JOIN)
SELECT p.nombre AS producto, pd.pedido_id
FROM pedido_detalle pd
RIGHT JOIN productos p ON pd.producto_id = p.id;



-- Mostrar cada producto con el total de veces que ha sido solicitado
SELECT p.nombre,
  (SELECT COUNT(*) FROM pedido_detalle pd WHERE pd.producto_id = p.id) AS total_veces_solicitado
FROM productos p;



-- Obtener usuarios que hayan realizado al menos un pedido
SELECT * FROM usuarios
WHERE id IN (SELECT usuario_id FROM pedido);



-- Listar todos los productos que tienen un precio mayor a 10.000, ordenados por precio descendente
SELECT * FROM productos
WHERE precio > 10000
ORDER BY precio DESC;



-- Contar cuántos pedidos tiene cada usuario
SELECT u.nombre, COUNT(pe.id) AS total_pedidos
FROM usuarios u
LEFT JOIN pedido pe ON u.id = pe.usuario_id
GROUP BY u.id;



-- Obtener el total y el promedio del precio de todos los productos
SELECT SUM(precio) AS total_precio, AVG(precio) AS promedio_precio
FROM productos;



-- Mostrar el nombre completo del producto con su precio
SELECT CONCAT(p.nombre, ' - $', p.precio) AS producto_precio
FROM productos p;



-- Listar todos los pedidos 'en_camino' con nombre del usuario y fecha del pedido
SELECT pe.id AS pedido_id, u.nombre AS usuario, pe.fecha_pedido
FROM pedido pe
JOIN usuarios u ON pe.usuario_id = u.id
WHERE pe.estado_pedido = 'en_camino';



-- Mostrar cada usuario con el total de productos que ha solicitado en todos sus pedidos
SELECT u.nombre,
  (SELECT SUM(pd.cantidad)
  FROM pedido pe
  JOIN pedido_detalle pd ON pe.id = pd.pedido_id
  WHERE pe.usuario_id = u.id) AS total_productos_solicitados
FROM usuarios u;



-- Obtener el producto más vendido con su nombre y total vendido
SELECT p.nombre, ventas.total_vendido
FROM productos p
JOIN (
  SELECT producto_id, SUM(cantidad) AS total_vendido
  FROM pedido_detalle
  GROUP BY producto_id
  ORDER BY total_vendido DESC
  LIMIT 1
) AS ventas ON p.id = ventas.producto_id;





