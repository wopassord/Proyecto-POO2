% Importar Robotics Toolbox de Peter Corke
clear, clc

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
Taux = IRB.fkine(q0).T;
coordenada0 = Taux(1:3,4);


% Configuración del servidor TCP/IP en MATLAB
server = tcpip('0.0.0.0', 8001, 'NetworkRole', 'server'); % Escuchar en todas las interfaces de red
set(server, 'InputBufferSize', 1024); % Tamaño del buffer de entrada
disp('Servidor MATLAB en espera de conexiones en el puerto 8001...');

% Ciclo infinito para recibir conexiones de clientes
while true
    fopen(server);  % Abrir conexión cuando haya un cliente disponible
    disp('Conexión establecida con el cliente.');

    % Generar un nombre de archivo GIF único para cada simulación
    timestamp = datestr(now, 'yyyymmdd_HHMMSS');
    gifFileName = ['robot_animation_', timestamp, '.gif'];
    save_gif = true;  % Variable de control para guardar en GIF
    gif_saved = false;  % Bandera de control para iniciar el GIF

    % Cerrar cualquier figura previa y crear una nueva
    close(gcf);  % Cierra la figura actual (si existe)
    figure;
    IRB.plot(q0, 'workspace', workspace_limits, 'trail', {'r', 'LineWidth', 2});
    view(35, 20);
    hold on;

    initial_position_set = false;  % Variable de control para la posición inicial
    T_current = transl(coordenada0);  % Posición inicial

    while true
        if server.BytesAvailable > 0
            message = fscanf(server);
            message = strtrim(message); % Elimina espacios o saltos de línea adicionales
            
            if strcmp(message, 'fin_gif')
                disp(['Guardado del GIF completado en ', gifFileName]);
                save_gif = false;  % Detener el guardado de fotogramas en el GIF
                break;  % Salir del bucle de simulación para esperar nuevas instrucciones
            elseif contains(message, ',')  % Verificar si es una coordenada
                try
                    coord = sscanf(message, '%f,%f,%f');
                    if length(coord) == 3
                        coord = coord * 0.001;  % Convertir a metros
                        disp(['Coordenadas recibidas: ', num2str(coord')]);

                        % Generar la trayectoria
                        T1 = T_current;
                        T2 = transl(coord(1), coord(2), coord(3));
                        trajectory = ctraj(T1, T2, 15);  % Ajusta el número de puntos según sea necesario
                        TrayectoriaTramo = zeros(15, 4);

                        for j = 1:15
                            q = IRB.ikine(trajectory(:,:,j), 'q0', TrayectoriaTramo(max(j-1,1), :), 'mask', [1 1 1 0 0 0]);
                            if isempty(q)
                                warning(['Cinemática inversa no converge para el punto ', num2str(j)]);
                                continue;
                            else
                                TrayectoriaTramo(j, :) = q;
                            end
                        end

                        % Animar y guardar en GIF
                        for i = 1:size(TrayectoriaTramo, 1)
                            IRB.animate(TrayectoriaTramo(i, :));
                            if save_gif
                                frame = getframe(gcf);  
                                im = frame2im(frame);   
                                [imind, cm] = rgb2ind(im, 256);
                                if ~gif_saved
                                    imwrite(imind, cm, gifFileName, 'gif', 'Loopcount', inf, 'DelayTime', 0.05);
                                    gif_saved = true;
                                else
                                    imwrite(imind, cm, gifFileName, 'gif', 'WriteMode', 'append', 'DelayTime', 0.05);
                                end
                            end
                        end

                        % Actualizar posición actual
                        T_current = T2;
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

    % Cerrar conexión y reiniciar en espera de un nuevo cliente
    fclose(server);
    disp('Esperando nueva conexión...');
end

