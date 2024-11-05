% Importar Robotics Toolbox de Peter Corke
% Asegúrate de tener la Toolbox instalada y en tu path de MATLAB
clear,clc
% Definir los parámetros de Denavit-Hartenberg (DH) para el IRB 460
L1 = Link('d', 0.050, 'a', 0, 'alpha', pi/2, 'qlim', [-180, 180]*pi/180);
L2 = Link('d', 0, 'a', 0.0605, 'alpha', 0, 'qlim', [-135, 90]*pi/180);
L3 = Link('d', 0, 'a', 0.120, 'alpha', 0, 'qlim', [-160, 280]*pi/180);
L4 = Link('d', 0, 'a', 0, 'alpha', 0, 'qlim', [-360, 360]*pi/180);

% Crear el objeto robot con SerialLink
IRB = SerialLink([L1 L2 L3 L4], 'name', 'IRB 460');

% Configurar los límites del espacio de trabajo
workspace_limits = [-0.2, 0.2, -0.2, 0.2, -0.1, 0.4];
q0 = [0, 0, 0, 0]; % Posición inicial en el espacio articular
Taux=IRB.fkine(q0).T;
coordenada0=Taux(1:3,4);
% Configurar la figura para la visualización
figure(1);
IRB.plot(q0, 'workspace', workspace_limits, 'trail', {'r', 'LineWidth', 2});
view(35, 20);
hold on;

% Configuración del servidor TCP/IP en MATLAB
server = tcpip('0.0.0.0', 3000, 'NetworkRole', 'server'); % Escuchar en todas las interfaces de red
fopen(server);  % Abrir conexión
disp('Servidor MATLAB escuchando en el puerto 3000...');

% Configurar el archivo GIF
gifFileName = 'robot_animation.gif';
save_gif = true;  % Variable de control para guardar en GIF

% Definir el número de puntos para la interpolación
num_points = 15;
initial_position_set = false;  % Variable de control para la posición inicial

% Ciclo infinito para recibir coordenadas continuamente
while true
    % Leer datos del cliente
    if server.BytesAvailable > 0
        message = fscanf(server);
        message = strtrim(message); % Elimina cualquier espacio o salto de línea adicional
        
        % Verificar si el mensaje es el comando de salida
        if strcmp(message, 'salir')
            disp('Cerrando servidor...');
            break;
        elseif strcmp(message, 'fin_gif')
            disp(['Finalizando guardado del GIF en ', gifFileName]);
            save_gif = false;
        else
            try
                % Intentar procesar el mensaje como coordenadas
                coord = sscanf(message, '%f,%f,%f');
                
                % Verificar que se hayan recibido tres valores
                if length(coord) == 3
                    disp(['Coordenadas recibidas: ', num2str(coord')]);

                    % Definir la posición inicial del robot si no se ha hecho
                    if ~initial_position_set
                        T1 = transl(coordenada0); % Posición inicial mediante cinemática directa
                        T2 = transl(coord(1), coord(2), coord(3));
                        
                        % Generar la trayectoria inicial desde T1 a T2
                        initial_trajectory = ctraj(T1, T2, num_points);

                        % Calcular la cinemática inversa para la trayectoria inicial
                        initial_trayectoria_tramo = zeros(num_points, 4);
                        for j = 1:num_points
                            initial_trayectoria_tramo(j, :) = IRB.ikine(initial_trajectory(:,:,j), 'q0', initial_trayectoria_tramo(max(j-1,1), :), 'mask', [1 1 1 0 0 0]);
                        end

                        % Animar la trayectoria inicial
                        for i = 1:size(initial_trayectoria_tramo, 1)
                            IRB.animate(initial_trayectoria_tramo(i, :));

                            % Guardar el fotograma en el GIF si está habilitado
                            if save_gif
                                frame = getframe(gcf);  % Captura el fotograma actual
                                im = frame2im(frame);   % Convierte el fotograma a una imagen
                                [imind, cm] = rgb2ind(im, 256);
                                if exist('gif_saved', 'var') == 0
                                    imwrite(imind, cm, gifFileName, 'gif', 'Loopcount', inf, 'DelayTime', 0.05);
                                    gif_saved = true; % Bandera para indicar que ya se inició el GIF
                                else
                                    imwrite(imind, cm, gifFileName, 'gif', 'WriteMode', 'append', 'DelayTime', 0.05);
                                end
                            end
                        end

                        % Marcar que la posición inicial ya fue procesada
                        initial_position_set = true;
                        T_current = T2;  % Establecer T2 como la posición actual
                    else
                        % Si ya se estableció la posición inicial, continuar con la trayectoria normal
                        T1 = T_current;
                        T2 = transl(coord(1), coord(2), coord(3));

                        % Generar la trayectoria en el espacio cartesiano entre T1 y T2
                        trajectory = ctraj(T1, T2, num_points);

                        % Inicializar la matriz de trayectoria articular
                        TrayectoriaTramo = zeros(num_points, 4);

                        % Calcular la cinemática inversa para obtener la trayectoria articular
                        for j = 1:num_points
                            TrayectoriaTramo(j, :) = IRB.ikine(trajectory(:,:,j), 'q0', TrayectoriaTramo(max(j-1,1), :), 'mask', [1 1 1 0 0 0]);
                        end

                        % Animar la trayectoria calculada y guardar en GIF
                        for i = 1:size(TrayectoriaTramo, 1)
                            IRB.animate(TrayectoriaTramo(i, :));

                            if save_gif
                                frame = getframe(gcf);  
                                im = frame2im(frame);   
                                [imind, cm] = rgb2ind(im, 256);
                                if exist('gif_saved', 'var') == 0
                                    imwrite(imind, cm, gifFileName, 'gif', 'Loopcount', inf, 'DelayTime', 0.05);
                                    gif_saved = true;
                                else
                                    imwrite(imind, cm, gifFileName, 'gif', 'WriteMode', 'append', 'DelayTime', 0.05);
                                end
                            end
                        end

                        % Actualizar la última posición alcanzada
                        T_current = T2;
                    end
                else
                    disp(['Error: Formato incorrecto de coordenadas. Recibido: ', message]);
                end
            catch ME
                disp(['Error al procesar las coordenadas: ', ME.message]);
            end
        end
    end
    
    pause(0.1);
end

% Cerrar la conexión al finalizar
fclose(server);
delete(server);
clear server;

disp('Servidor cerrado.');

