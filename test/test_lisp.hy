(alias triangle
       (polygon 3
                ["fill" (color 0 0 0 0)]
                ["stroke" (color 1 1 0)]
                ["line" 0.05]
                ["radius" 0.5]))

(layer render
       (group
         [(group
            [(polygon 4
                      ["fill" (color 0 1 1)]
                      ["rotation" (/ pi 4)]
                      ["position" 0.5 0]
                      ["radius" 0.5])

             (polygon 8
                      ["radius" 0.2]
                      ["stroke" (color 0 0 1)])]

            ["line" 0.05]
            ["fill" (color 0.5)]
            ["stroke" (color 0 1 0)])

          (triangle)]

         ["rotate" (/ pi 6)]))

(window "master"
        (render))

(window "overwiew"
        (render))
